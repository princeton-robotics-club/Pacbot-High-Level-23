import pygame
from pygame.locals import *
from constants import UP, DOWN, LEFT, RIGHT
import sys
import time


class Visualizer(object):
    def __init__(self):
        # image dimensions in pixels
        self.IMAGE_SIZE = 32 / 2  # actual size / scaling factor to make screen fit
        # grid dimensions for drawing
        GRID_WIDTH = 33
        GRID_HEIGHT = 28
        pygame.init()

        self.screen = pygame.display.set_mode(
            ((GRID_WIDTH + 8) * self.IMAGE_SIZE, GRID_HEIGHT * self.IMAGE_SIZE)
        )
        self.maze_end = (GRID_WIDTH - 1) * self.IMAGE_SIZE
        self.font = pygame.font.SysFont(None, 24)
        self.state_mappings = {1: "Scatter", 2: "Chase", 3: "Frightened"}
        # screen = pygame.display.set_mode((screen_width, screen_height), HWSURFACE|DOUBLEBUF|RESIZABLE)
        # fake_screen = screen.copy()
        pacbot = pygame.transform.scale(
            pygame.image.load("static/pacman_c.png").convert(),
            (self.IMAGE_SIZE, self.IMAGE_SIZE),
        )
        r_ghost = pygame.transform.scale(
            pygame.image.load("static/ghost1.png").convert(),
            (self.IMAGE_SIZE, self.IMAGE_SIZE),
        )
        p_ghost = pygame.transform.scale(
            pygame.image.load("static/ghost4.png").convert(),
            (self.IMAGE_SIZE, self.IMAGE_SIZE),
        )
        o_ghost = pygame.transform.scale(
            pygame.image.load("static/ghost3.png").convert(),
            (self.IMAGE_SIZE, self.IMAGE_SIZE),
        )
        b_ghost = pygame.transform.scale(
            pygame.image.load("static/ghost2.png").convert(),
            (self.IMAGE_SIZE, self.IMAGE_SIZE),
        )
        wall = pygame.transform.scale(
            pygame.image.load("static/wall.png").convert(),
            (self.IMAGE_SIZE, self.IMAGE_SIZE),
        )
        pellet = pygame.transform.scale(
            pygame.image.load("static/dot.png").convert(),
            (self.IMAGE_SIZE, self.IMAGE_SIZE),
        )
        power_pellet = pygame.transform.scale(
            pygame.image.load("static/power.png").convert(),
            (self.IMAGE_SIZE, self.IMAGE_SIZE),
        )
        ghost_frightened = pygame.transform.scale(
            pygame.image.load("static/ghost_white.png").convert(),
            (self.IMAGE_SIZE, self.IMAGE_SIZE),
        )
        self.grid_legend = {
            "a": pacbot,
            "r": r_ghost,
            "p": p_ghost,
            "o": o_ghost,
            "b": b_ghost,
            "#": wall,
            "-": pellet,
            "%": power_pellet,
            "f": ghost_frightened,
        }
        self.angles = {UP: 90, LEFT: 180, RIGHT: 0, DOWN: 270}
        self.curr_angle = 90

    def draw_grid(self, grid, orientation, game_state=None, lives=None):
        self.screen.fill(((0, 0, 0)))
        pacbot = self.grid_legend["a"]
        angle_change = self.angles[orientation] - self.curr_angle
        self.curr_angle = self.angles[orientation]
        self.grid_legend["a"] = pygame.transform.rotate(pacbot, angle_change)
        for row, row_vals in enumerate(grid):
            for cell, cell_val in enumerate(row_vals):
                # print((row * self.self.IMAGE_SIZE, cell * self.self.IMAGE_SIZE))
                tile = self.grid_legend.get(cell_val)
                if tile:
                    self.screen.blit(
                        tile, (cell * self.IMAGE_SIZE, row * self.IMAGE_SIZE)
                    )
        if game_state is not None:
            img = self.font.render(
                f"State: {self.state_mappings[game_state]}", True, (0, 0, 255)
            )
            self.screen.blit(img, (self.maze_end, 20))
        if lives is not None:
            img = self.font.render(f"Lives: {lives}", True, (0, 0, 255))
            self.screen.blit(img, (self.maze_end, 40))
        pygame.display.update()

    def wait_manual_control(self):
        # blocks code until key is pressed
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    return event.key

    def wait_ai_control(self):
        # only blocks if the space key is pressed
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == pygame.K_SPACE:
                    while True:
                        key_pressed = self.wait_manual_control()
                        if key_pressed in {pygame.K_SPACE, pygame.K_q}:
                            return key_pressed
                return event.key
