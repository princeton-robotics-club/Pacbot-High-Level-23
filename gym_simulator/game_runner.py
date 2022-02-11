# testing to see if I can interactively run the game

from gameState import GameState 
from stateConverter import StateConverter
from grid import grid
from variables import *

import numpy as np

RIGHT = "d"
LEFT = "a"
UP = "w"
DOWN = "s"
STAY = " "

if __name__ == "__main__":
    
    PELLET_LOCATIONS = 1*(np.array(grid) == o)
    PELLET_LOCATIONS *= PELLET_LOCATIONS.cumsum().reshape(PELLET_LOCATIONS.shape)

    POWER_PELLET_LOCATIONS = 1*(np.array(grid) == O)
    POWER_PELLET_LOCATIONS *= POWER_PELLET_LOCATIONS.cumsum().reshape(POWER_PELLET_LOCATIONS.shape)

    #print()

    #print(PELLET_LOCATIONS)
    #print(POWER_PELLET_LOCATIONS)
    #quit()
    #print((np.array(grid, dtype=str)))
    #print(1*(np.array(grid, dtype=str) == "o"))
    #quit()
    game_state = GameState()
    print(game_state.red.pos)
    print(game_state.pink.pos)
    print(game_state.orange.pos)
    print(game_state.blue.pos)
    quit()

    print(type(game_state.pacbot.pos))
    quit()
    print(np.array(game_state.grid))
    light_state = StateConverter().convert_game_state_to_light(game_state)
    full_state = StateConverter().convert_game_state_to_full(game_state)

    print(type(game_state.grid))
    quit()
    print(full_state)
    print(light_state)

    print(full_state.mode)
    print(full_state.frightened_timer)
    for i in range(10):
        print(input())
    quit()
    proto.mode = StateConverter._parse_game_mode(game_state.state, game_state.play)
    proto.frightened_timer = game_state.frightened_counter
    proto.score = game_state.score
    proto.grid_columns = len(game_state.grid[0])
    proto.lives = game_state.lives
    proto.update_ticks = (game_state.update_ticks - 1) % ticks_per_update
    proto.ticks_per_update = ticks_per_update
    proto.elapsed_time = game_state.elapsed_time

    if game_state.play:
        proto.elapsed_time += time.time() - game_state.previous_start

    proto.red_ghost.x = game_state.red.pos['current'][0]
    proto.red_ghost.y = game_state.red.pos['current'][1]
    proto.red_ghost.direction = StateConverter._directions[game_state.red.direction]
    proto.red_ghost.frightened_counter = game_state.red.frightened_counter

    proto.pink_ghost.x = game_state.pink.pos['current'][0]
    proto.pink_ghost.y = game_state.pink.pos['current'][1]
    proto.pink_ghost.direction = StateConverter._directions[game_state.pink.direction]
    proto.pink_ghost.frightened_counter = game_state.pink.frightened_counter

    proto.orange_ghost.x = game_state.orange.pos['current'][0]
    proto.orange_ghost.y = game_state.orange.pos['current'][1]
    proto.orange_ghost.direction = StateConverter._directions[game_state.orange.direction]
    proto.orange_ghost.frightened_counter = game_state.orange.frightened_counter

    proto.blue_ghost.x = game_state.blue.pos['current'][0]
    proto.blue_ghost.y = game_state.blue.pos['current'][1]
    proto.blue_ghost.direction = StateConverter._directions[game_state.blue.direction]
    proto.blue_ghost.frightened_counter = game_state.blue.frightened_counter

    proto.pacman.x = game_state.pacbot.pos[0]
    proto.pacman.y = game_state.pacbot.pos[1]
    proto.pacman.direction = StateConverter._directions[game_state.pacbot.direction]

    for col in game_state.grid:
        for el in col:
            proto.grid.append(StateConverter._parse_grid_element(el))