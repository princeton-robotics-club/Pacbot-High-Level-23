import pygame
from pygame.locals import *
import sys


class Visualizer(object):
    
    # image dimensions in pixels
    IMAGE_SIZE = 32
    # grid dimensions for drawing
    GRID_WIDTH = 28
    GRID_HEIGHT = 32
    pygame.init()

    screen = pygame.display.set_mode((GRID_WIDTH * IMAGE_SIZE, GRID_HEIGHT * IMAGE_SIZE))
    pacbot = pygame.image.load("static/pacman_c.png").convert()
    r_ghost = pygame.image.load("static/ghost1.png").convert()
    p_ghost = pygame.image.load("static/ghost4.png").convert()
    o_ghost = pygame.image.load("static/ghost3.png").convert()
    b_ghost = pygame.image.load("static/ghost2.png").convert()
    wall = pygame.image.load("static/wall.png").convert()
    pellet = pygame.image.load("static/dot.png").convert()
    power_pellet = pygame.image.load("static/power.png").convert()
    grid_legend = {
        "a": pacbot,
        "r": r_ghost,
        "p": p_ghost,
        "o": o_ghost,
        "b": b_ghost,
        "#": wall,
        "-": pellet,
        "%": power_pellet,
    }
    screen.fill(((255, 255, 255)))
    def draw_grid(self, grid):
        self.screen.fill(((0, 0, 0)))
        for row, row_vals in enumerate(grid):
            for cell, cell_val in enumerate(row_vals):
                #print((row * self.IMAGE_SIZE, cell * self.IMAGE_SIZE))
                tile = self.grid_legend.get(cell_val)
                if tile:
                    self.screen.blit(tile, (row * self.IMAGE_SIZE, cell * self.IMAGE_SIZE))
        self.screen.blit(self.pacbot, (0, 0))
        pygame.display.update()
    def wait(self):
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    return pygame.key.name(event.key)
    def wait2(self):
        pygame.event.get()