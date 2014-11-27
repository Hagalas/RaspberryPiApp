#!/usr/bin/env python2
# -*- coding: utf-8 -*-


from main import pygame
from main import RES
from gameState import GameState


class Player(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = (34, 31)
        self.rect = self.image.get_rect()
        self.rect.x = (RES[0] / 2) - (self.size[0] / 2)
        self.rect.y = 520
        self.travel = 17
        self.speed = 350
        self.time = pygame.time.get_ticks()

    def update(self):
        self.rect.x += GameState.vector * self.travel
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > RES[0] - self.size[0]:
            self.rect.x = RES[0] - self.size[0]
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > RES[1] - self.size[1]:
            self.rect.y = RES[1] - self.size[1]