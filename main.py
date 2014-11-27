#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pygame, random, os
import player
from ammo import Ammo
from enemy import Enemy
from block import Block
from gameState import GameState

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ENEMY_SIZE = (30, 40)
ENEMY_SPACER = 20
BARRIER_ROW = 10
BARRIER_COLUMN = 4
BULLET_SIZE = (3, 10)
MISSILE_SIZE = (5, 5)
BLOCK_SIZE = [10, 10]
RES = (800, 600)
CUR_DIR = os.path.dirname(os.path.abspath(__file__))


class Game(object):
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.game_font = pygame.font.SysFont('ActionIsShaded', 28)
        self.intro_font = pygame.font.SysFont('ActionIsShaded', 72)
        self.screen = pygame.display.set_mode([RES[0], RES[1]])
        self.time = pygame.time.get_ticks()
        self.refresh_rate = 20
        self.rounds_won = 0
        self.level_up = 50
        self.score = 0
        self.lives = 4
        self.player_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.missile_group = pygame.sprite.Group()
        self.barrier_group = pygame.sprite.Group()
        self.all_sprite_list = pygame.sprite.Group()
        self.intro_screen = pygame.image.load(os.path.join(CUR_DIR, 'data/graphics/start_screen.jpg')).convert()
        self.intro_logo = pygame.image.load(os.path.join(CUR_DIR, 'data/graphics/logo.png')).convert_alpha()
        self.background = pygame.image.load(os.path.join(CUR_DIR, 'data/graphics/background.png')).convert()
        pygame.display.set_caption('Angry LLAMa - ESC by wyjsc')
        pygame.mouse.set_visible(False)
        Enemy.image = pygame.image.load(os.path.join(CUR_DIR, 'data/graphics/enemy.png')).convert_alpha()
        Enemy.image.set_colorkey(WHITE)
        self.ani_pos = 1
        self.ship_sheet = pygame.image.load(os.path.join(CUR_DIR, 'data/graphics/lama.png')).convert_alpha()
        player.Player.image = self.ship_sheet.subsurface(self.ani_pos * 64, 0, 64, 61)
        self.animate_up = False
        self.animate_down = False
        self.animate_right = False
        self.animate_left = False
        self.explosion_sheet = pygame.image.load(os.path.join(CUR_DIR, 'data/graphics/explosion_new1.png')).convert_alpha()
        self.explosion_image = self.explosion_sheet.subsurface(0, 0, 79, 96)
        self.enemy_explosion_sheet = pygame.image.load(os.path.join(CUR_DIR, 'data/graphics/enemy_explosion.png'))
        self.enemy_explode_graphics = self.enemy_explosion_sheet.subsurface(0, 0, 94, 96)
        self.explode = False
        self.explode_pos = 0
        self.enemy_explode = False
        self.enemy_explode_pos = 0
        self.explodey_enemy = []

    def control(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameState.start_screen = False
                GameState.end_game = True
            if event.type == pygame.KEYDOWN \
                    and event.key == pygame.K_ESCAPE:
                if GameState.start_screen:
                    GameState.start_screen = False
                    GameState.end_game = True
                    self.kill_all()
                else:
                    GameState.start_screen = True
        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_LEFT]:
            GameState.vector = -1
            self.animate_up = False
            self.animate_down = False
            self.animate_left = True
            self.animate_right = False
        elif self.keys[pygame.K_RIGHT]:
            GameState.vector = 1
            self.animate_up = False
            self.animate_down = False
            self.animate_right = True
            self.animate_left = False
        elif self.keys[pygame.K_UP]:
            self.player.rect.y -= 20
            self.animate_up = True
            self.animate_down = False
            self.animate_right = False
            self.animate_left = False
        elif self.keys[pygame.K_DOWN]:
            self.player.rect.y += 20
            self.animate_up = False
            self.animate_down = True
            self.animate_right = False
            self.animate_left = False

        else:
            GameState.vector = 0
            self.animate_up = False
            self.animate_down = False
            self.animate_right = False
            self.animate_left = False

        if self.keys[pygame.K_SPACE]:
            if GameState.start_screen:
                GameState.start_screen = False
                self.lives = 4
                self.score = 0
                self.make_player()
                self.make_defenses()
                self.enemy_wave(0)
            else:
                GameState.shoot_bullet = True
                # self.bullet_fx.play()
        if self.keys[pygame.K_z]:
            self.win_round()
            self.next_round()

    def animate_player(self):
        if self.animate_right:
            if self.ani_pos < 2:
                player.Player.image = self.ship_sheet.subsurface(self.ani_pos * 64, 0, 64, 61)
                self.ani_pos += 1
        else:
            if self.ani_pos > 0:
                self.ani_pos -= 1
                player.Player.image = self.ship_sheet.subsurface(self.ani_pos * 64, 0, 64, 61)

        if self.animate_left:
            if self.ani_pos > 0:
                self.ani_pos -= 1
                player.Player.image = self.ship_sheet.subsurface(self.ani_pos * 64, 0, 64, 61)
        else:
            if self.ani_pos < 2:
                player.Player.image = self.ship_sheet.subsurface(self.ani_pos * 64, 0, 64, 61)
                self.ani_pos += 1

    def player_explosion(self):
        if self.explode:
            if self.explode_pos < 8:
                self.explosion_image = self.explosion_sheet.subsurface(0, self.explode_pos * 96, 79, 96)
                self.explode_pos += 1
                self.screen.blit(self.explosion_image, [self.player.rect.x - 10, self.player.rect.y - 30])
            else:
                self.explode = False
                self.explode_pos = 0

    def enemy_explosion(self):
        if self.enemy_explode:
            if self.enemy_explode_pos < 9:
                self.enemy_explode_graphics = self.enemy_explosion_sheet.subsurface(
                    0, self.enemy_explode_pos * 96, 94, 96)
                self.enemy_explode_pos += 1
                self.screen.blit(self.enemy_explode_graphics, [
                    int(self.explodey_enemy[0]) - 50, int(self.explodey_enemy[1]) - 60])
            else:
                self.enemy_explode = False
                self.enemy_explode_pos = 0
                self.explodey_enemy = []

    def splash_screen(self):
        while GameState.start_screen:
            self.kill_all()
            self.screen.blit(self.intro_screen, [0, 0])
            self.screen.blit(self.intro_logo, [8, 50])
            self.screen.blit(self.game_font.render(
                "Wcisnij Spacje by zagrac", 1, WHITE), (14, 261))
            pygame.display.flip()
            self.control()
            self.clock.tick(self.refresh_rate / 2)

    def make_player(self):
        self.player = player.Player()
        self.player_group.add(self.player)
        self.all_sprite_list.add(self.player)

    def refresh_screen(self):
        self.all_sprite_list.draw(self.screen)
        self.animate_player()
        self.player_explosion()
        self.enemy_explosion()
        self.refresh_scores()
        pygame.display.flip()
        self.screen.blit(self.background, [0, 0])
        self.clock.tick(self.refresh_rate)

    def refresh_scores(self):
        self.screen.blit(self.game_font.render(
            "WYNIK " + str(self.score), 1, WHITE), (10, 8))
        self.screen.blit(self.game_font.render(
            "SZANSE " + str(self.lives + 1), 1, RED), (355, 575))

    def enemy_wave(self, speed):
        for column in range(BARRIER_COLUMN):
            for row in range(BARRIER_ROW):
                enemy = Enemy()
                enemy.rect.y = 65 + (column * (
                    ENEMY_SIZE[1] + ENEMY_SPACER))
                enemy.rect.x = ENEMY_SPACER + (
                    row * (ENEMY_SIZE[0] + ENEMY_SPACER))
                self.enemy_group.add(enemy)
                self.all_sprite_list.add(enemy)
                enemy.speed -= speed

    def make_bullet(self):
        if GameState.game_time - self.player.time > self.player.speed:
            bullet = Ammo(WHITE, BULLET_SIZE)
            bullet.vector = -1
            bullet.speed = 56
            bullet.rect.x = self.player.rect.x + 28
            bullet.rect.y = self.player.rect.y
            self.bullet_group.add(bullet)
            self.all_sprite_list.add(bullet)
            self.player.time = GameState.game_time
        GameState.shoot_bullet = False

    def make_missile(self):
        if len(self.enemy_group):
            shoot = random.random()
            if shoot <= 0.05:
                shooter = random.choice([
                    enemy for enemy in self.enemy_group])
                missile = Ammo(RED, MISSILE_SIZE)
                missile.vector = 1
                missile.rect.x = shooter.rect.x + 15
                missile.rect.y = shooter.rect.y + 40
                missile.speed = 10
                self.missile_group.add(missile)
                self.all_sprite_list.add(missile)

    def make_barrier(self, columns, rows, spacer):
        for column in range(columns):
            for row in range(rows):
                barrier = Block(WHITE, (BLOCK_SIZE))
                barrier.rect.x = 35 + (200 * spacer) + (row * 10)
                barrier.rect.y = 450 + (column * 10)
                self.barrier_group.add(barrier)
                self.all_sprite_list.add(barrier)

    def make_defenses(self):
        for spacing, spacing in enumerate(xrange(4)):
            self.make_barrier(3, 9, spacing)

    def kill_all(self):
        for items in [self.bullet_group, self.player_group,
                      self.enemy_group, self.missile_group, self.barrier_group]:
            for i in items:
                i.kill()

    def is_dead(self):
        if self.lives < 0:
            self.screen.blit(self.game_font.render(
                "Przegrales! Twoj wynik to: " + str(
                    self.score), 1, RED), (250, 15))
            self.rounds_won = 0
            self.refresh_screen()
            self.level_up = 50
            self.explode = False
            self.enemy_explode = False
            pygame.time.delay(3000)
            return True

    def defenses_breached(self):
        for enemy in self.enemy_group:
            if enemy.rect.y > 410:
                self.screen.blit(self.game_font.render(
                    "Wsciekle ptaki Cie rozwalily!",
                    1, RED), (180, 15))
                self.refresh_screen()
                self.level_up = 50
                self.explode = False
                self.enemy_explode = False
                pygame.time.delay(3000)
                return True

    def win_round(self):
        if len(self.enemy_group) < 1:
            self.rounds_won += 1
            self.screen.blit(self.game_font.render(
                "Wygrales runde " + str(self.rounds_won) +
                "  ale walka trwa nadal", 1, RED), (200, 15))
            self.refresh_screen()
            pygame.time.delay(3000)
            return True

    def next_round(self):
        BLOCK_SIZE[0]-=2
        BLOCK_SIZE[1]-=2
        self.explode = False
        self.enemy_explode = False
        for actor in [self.missile_group,
                      self.barrier_group, self.bullet_group]:
            for i in actor:
                i.kill()
        self.enemy_wave(self.level_up)
        self.make_defenses()
        self.level_up += 50

    def calc_collisions(self):
        pygame.sprite.groupcollide(
            self.missile_group, self.barrier_group, True, True)
        pygame.sprite.groupcollide(
            self.bullet_group, self.barrier_group, True, True)

        for z in pygame.sprite.groupcollide(
                self.bullet_group, self.enemy_group, True, True):
            self.enemy_explode = True
            self.explodey_enemy.append(z.rect.x)
            self.explodey_enemy.append(z.rect.y)
            self.score += 10

        if pygame.sprite.groupcollide(
                self.player_group, self.missile_group, False, True):
            self.lives -= 1
            self.explode = True

    def main_loop(self):
        while not GameState.end_game:
            while not GameState.start_screen:
                GameState.game_time = pygame.time.get_ticks()
                GameState.enemy_time = pygame.time.get_ticks()
                self.control()
                self.make_missile()
                self.calc_collisions()
                self.refresh_screen()
                if self.is_dead() or self.defenses_breached():
                    GameState.start_screen = True
                for actor in [self.player_group, self.bullet_group,
                              self.enemy_group, self.missile_group]:
                    for i in actor:
                        i.update()
                if GameState.shoot_bullet:
                    self.make_bullet()
                if self.win_round():
                    self.next_round()
            self.splash_screen()
        pygame.quit()


if __name__ == '__main__':
    pv = Game()
    pv.main_loop()