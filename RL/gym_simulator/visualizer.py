import pygame
from pygame.locals import *
import sys
import time


class Visualizer(object):
    def __init__(self):
        # image dimensions in pixels
        self.IMAGE_SIZE = 32 / 2 # actual size / scaling factor to make screen fit
        # grid dimensions for drawing
        GRID_WIDTH = 33
        GRID_HEIGHT = 28
        pygame.init()
        infoObj = pygame.display.Info()
        screen_width, screen_height = infoObj.current_w, infoObj.current_h
        self.screen = pygame.display.set_mode((GRID_WIDTH * self.IMAGE_SIZE, GRID_HEIGHT * self.IMAGE_SIZE))
        #screen = pygame.display.set_mode((screen_width, screen_height), HWSURFACE|DOUBLEBUF|RESIZABLE)
        #fake_screen = screen.copy()
        pacbot = pygame.transform.scale(pygame.image.load("static/pacman_c.png").convert(), (self.IMAGE_SIZE, self.IMAGE_SIZE))
        r_ghost = pygame.transform.scale(pygame.image.load("static/ghost1.png").convert(), (self.IMAGE_SIZE, self.IMAGE_SIZE))
        p_ghost = pygame.transform.scale(pygame.image.load("static/ghost4.png").convert(), (self.IMAGE_SIZE, self.IMAGE_SIZE))
        o_ghost = pygame.transform.scale(pygame.image.load("static/ghost3.png").convert(), (self.IMAGE_SIZE, self.IMAGE_SIZE))
        b_ghost = pygame.transform.scale(pygame.image.load("static/ghost2.png").convert(), (self.IMAGE_SIZE, self.IMAGE_SIZE))
        wall = pygame.transform.scale(pygame.image.load("static/wall.png").convert(), (self.IMAGE_SIZE, self.IMAGE_SIZE))
        pellet = pygame.transform.scale(pygame.image.load("static/dot.png").convert(), (self.IMAGE_SIZE, self.IMAGE_SIZE))
        power_pellet = pygame.transform.scale(pygame.image.load("static/power.png").convert(), (self.IMAGE_SIZE, self.IMAGE_SIZE))
        ghost_frightened = pygame.transform.scale(pygame.image.load("static/ghost_white.png").convert(), (self.IMAGE_SIZE, self.IMAGE_SIZE))
        self.grid_legend = {
            "a": pacbot,
            "r": r_ghost,
            "p": p_ghost,
            "o": o_ghost,
            "b": b_ghost,
            "#": wall,
            "-": pellet,
            "%": power_pellet,
            "f": ghost_frightened
        }

    def draw_grid(self, grid):
        self.screen.fill(((0, 0, 0)))
        for row, row_vals in enumerate(grid):
            for cell, cell_val in enumerate(row_vals):
                #print((row * self.self.IMAGE_SIZE, cell * self.self.IMAGE_SIZE))
                tile = self.grid_legend.get(cell_val)
                if tile:
                    self.screen.blit(tile, (cell * self.IMAGE_SIZE, row * self.IMAGE_SIZE))
        #self.screen.blit(pygame.transform.scale(self.fake_screen, self.screen.get_rect().size), (0,0))
        pygame.display.update()
        
    def wait(self):
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    return pygame.key.name(event.key)
    def wait2(self):
        pygame.event.get()
        #time.sleep(0.5)