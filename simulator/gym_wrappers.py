import numpy as np
import gym
from gym import spaces 

from .game_engine.gameState import GameState
from .game_engine.grid import grid
from .game_engine.variables import *

"""
game state is [
    mode, lives, cherry, frightened_timer,
    pacman_x, pacman_y, pacman_direction,                                                                  # x, y = row, col
    red_ghost_x, red_ghost_y, red_direction, red_ghost_frightened, red_frightened_counter,
    pink_ghost_x, pink_ghost_y, pink_direction, pink_ghost_frightened, pink_frightened_counter,
    orange_ghost_x, orange_ghost_y, orange_direction, orange_ghost_frightened, orange_frightened_counter,
    blue_ghost_x, blue_ghost_y, blue_direction, blue_ghost_frightened, blue_frightened_counter,
    pellet_1, ..., pellet_240,                                                                             # whether the corresponding pellet is present
    power_pellet_1, ..., power_pellet_4,                                                                   # whether the corresponding power pellet is present
]
"""
class PacBotEnv(gym.Env):
    metadata = {"render.modes": ["console"]}

    DEATH_REWARD = -50
    LOSE_REWARD = -50
    WIN_REWARD = 100
    STEP_REWARD = -0.1

    UP = 0
    LEFT = 1
    STAY = 2
    RIGHT = 3
    DOWN = 4
    NUM_ACTIONS = 5

    GRID_HEIGHT, GRID_WIDTH = np.shape(grid)

    PELLET_LOCATIONS = 1*(np.array(grid) == o)
    PELLET_LOCATIONS *= PELLET_LOCATIONS.cumsum().reshape(PELLET_LOCATIONS.shape)

    POWER_PELLET_LOCATIONS = 1*(np.array(grid) == O)
    POWER_PELLET_LOCATIONS *= POWER_PELLET_LOCATIONS.cumsum().reshape(POWER_PELLET_LOCATIONS.shape)

    NUM_PELLETS = np.sum(PELLET_LOCATIONS != 0)
    NUM_POWER_PELLETS = np.sum(POWER_PELLET_LOCATIONS != 0)

    WALL_LOCATIONS = np.array(grid) == I
    GHOST_SPAWN = np.array(grid) == n
    BAD_LOCATIONS = WALL_LOCATIONS + GHOST_SPAWN

    STATE_VALUES = [
        "mode", "lives", "cherry", "frightened_timer",
        "pac_x", "pac_y", "pac_dir",
        "r_x", "r_y", "r_dir", "r_frightened", "r_frightened_counter",
        "p_x", "p_y", "p_dir", "p_frightened", "p_frightened_counter",
        "o_x", "o_y", "o_dir", "o_frightened", "o_frightened_counter",
        "b_x", "b_y", "b_dir", "b_frightened", "b_frightened_counter",
    ]
    STATE_VALUES.extend(["pellet" for i in range(NUM_PELLETS)])
    STATE_VALUES.extend(["power_pellet" for i in range(NUM_POWER_PELLETS)])
    STATE_SHAPE = np.shape(STATE_VALUES)
    STATE_VALUE_MIN = 0
    STATE_VALUE_MAX = 40
    
    def __init__(self, speed=1):
        super(PacBotEnv, self).__init__()

        self.action_space = spaces.Discrete(self.NUM_ACTIONS)
        self.observation_space = spaces.Box(low=self.STATE_VALUE_MIN, high=self.STATE_VALUE_MAX, shape=self.STATE_SHAPE, dtype=np.float32)

        self.next_step_rate = int(speed*ticks_per_update)

        self.game_state = GameState()

        self.running_score = 0
        self.prev_reward = 0
        self.prev_done = False
        self.num_lives = self.game_state.lives

    def _get_state(self):
        game_state = self.game_state
        STATE_VALUES = self.STATE_VALUES 
        PELLET_LOCATIONS = self.PELLET_LOCATIONS
        POWER_PELLET_LOCATIONS = self.POWER_PELLET_LOCATIONS

        state = np.zeros(self.STATE_SHAPE)

        state[STATE_VALUES.index("mode")] = game_state.state
        state[STATE_VALUES.index("lives")] = game_state.lives
        state[STATE_VALUES.index("cherry")] = game_state.cherry
        state[STATE_VALUES.index("frightened_timer")] = game_state.frightened_counter

        state[STATE_VALUES.index("pac_x")] = game_state.pacbot.pos[0]
        state[STATE_VALUES.index("pac_y")] = game_state.pacbot.pos[1]
        state[STATE_VALUES.index("pac_dir")] = game_state.pacbot.direction

        state[STATE_VALUES.index("r_x")] = game_state.red.pos['current'][0]
        state[STATE_VALUES.index("r_y")] = game_state.red.pos['current'][1]
        state[STATE_VALUES.index("r_dir")] = game_state.red.direction
        state[STATE_VALUES.index("r_frightened")] = 1 if game_state.red.frightened_counter > 0 else 0
        state[STATE_VALUES.index("r_frightened_counter")] = game_state.red.frightened_counter

        state[STATE_VALUES.index("p_x")] = game_state.pink.pos['current'][0]
        state[STATE_VALUES.index("p_y")] = game_state.pink.pos['current'][1]
        state[STATE_VALUES.index("p_dir")] = game_state.pink.direction
        state[STATE_VALUES.index("p_frightened")] = 1 if game_state.pink.frightened_counter > 0 else 0
        state[STATE_VALUES.index("p_frightened_counter")] = game_state.pink.frightened_counter

        state[STATE_VALUES.index("o_x")] = game_state.orange.pos['current'][0]
        state[STATE_VALUES.index("o_y")] = game_state.orange.pos['current'][1]
        state[STATE_VALUES.index("o_dir")] = game_state.orange.direction
        state[STATE_VALUES.index("o_frightened")] = 1 if game_state.orange.frightened_counter > 0 else 0
        state[STATE_VALUES.index("o_frightened_counter")] = game_state.orange.frightened_counter

        state[STATE_VALUES.index("b_x")] = game_state.blue.pos['current'][0]
        state[STATE_VALUES.index("b_y")] = game_state.blue.pos['current'][1]
        state[STATE_VALUES.index("b_dir")] = game_state.blue.direction
        state[STATE_VALUES.index("b_frightened")] = 1 if game_state.blue.frightened_counter > 0 else 0
        state[STATE_VALUES.index("b_frightened_counter")] = game_state.blue.frightened_counter

        state[np.array(STATE_VALUES) == "pellet"] = np.array(game_state.grid)[PELLET_LOCATIONS != 0] == o
        state[np.array(STATE_VALUES) == "power_pellet"] = np.array(game_state.grid)[POWER_PELLET_LOCATIONS != 0] == O

        return state
        
    """ 
    returns game state as numpy array
    """
    def reset(self):
        self.game_state.restart()
        self.game_state.unpause()
        self.running_score = 0
        self.prev_reward = 0
        self.prev_done = False
        self.num_lives = self.game_state.lives
        return self._get_state()

    def step(self, action):
        if self.prev_done:
            self.reset()

        game_state = self.game_state

        # accounts for different engine speeds
        for i in range(self.next_step_rate):
            game_state.next_step()

        reward = game_state.score - self.running_score
        self.running_score = game_state.score
        
        # indicates that the pacbot has lost a life
        if self.num_lives != game_state.lives:
            reward = self.DEATH_REWARD
            self.num_lives = game_state.lives

        done = game_state.game_over
        if done:
            # set reward to lose reward if pellets still remain
            if (np.array(game_state.grid) == o).any() or (np.array(game_state.grid) == O).any():
                reward = self.LOSE_REWARD
            # otherwise set reward to win reward
            else:
                reward = self.WIN_REWARD

        reward += self.STEP_REWARD
        self.prev_reward = reward
        self.prev_done = done

        old_pac_pos = game_state.pacbot.pos # (row, col)

        if action == self.UP:
            new_pac_pos = (old_pac_pos[0] - 1, old_pac_pos[1])

        elif action == self.LEFT:
            new_pac_pos = (old_pac_pos[0], old_pac_pos[1] - 1)

        elif action == self.STAY:
            new_pac_pos = (old_pac_pos[0], old_pac_pos[1])

        elif action == self.RIGHT:
            new_pac_pos = (old_pac_pos[0], old_pac_pos[1] + 1)

        elif action == self.DOWN:
            new_pac_pos = (old_pac_pos[0] + 1, old_pac_pos[1])

        else:
            raise ValueError("Received invalid action={} which is not part of the action space.".format(action))

        # handles invalid new positions
        if self.WALL_LOCATIONS[new_pac_pos[0], new_pac_pos[1]] != 0:
            new_pac_pos = old_pac_pos
        
        game_state.pacbot.update(new_pac_pos)

        # return state, reward, done, info
        return self._get_state(), reward, done, {}

    def render(self, mode='console'):
        if mode != 'console':
            raise NotImplementedError()

        STATE_VALUES = self.STATE_VALUES
        
        state = self._get_state()
        
        pacbot = "a"
        r_ghost = "r"
        p_ghost = "p"
        o_ghost = "o"
        b_ghost = "b"
        frightened_ghost = "f"
        wall = "#"
        pellet = "-"
        power_pellet = "%"

        grid = np.zeros((self.GRID_HEIGHT, self.GRID_WIDTH), dtype=str)
        grid[:, :] = ' '

        # fill in grid
        grid[self.WALL_LOCATIONS != 0] = wall

        pellet_exists = state[np.array(STATE_VALUES) == "pellet"]
        for i in range(len(pellet_exists)):
            if pellet_exists[i]:
                grid[self.PELLET_LOCATIONS == i+1] = pellet

        power_pellet_exists = state[np.array(STATE_VALUES) == "power_pellet"]
        for i in range(len(power_pellet_exists)):
            if power_pellet_exists[i]:
                grid[self.POWER_PELLET_LOCATIONS == i+1] = power_pellet

        r_frightened = state[STATE_VALUES.index("r_frightened")]
        p_frightened = state[STATE_VALUES.index("p_frightened")]
        o_frightened = state[STATE_VALUES.index("o_frightened")]
        b_frightened = state[STATE_VALUES.index("b_frightened")]
        
        grid[int(state[STATE_VALUES.index("pac_x")]), int(state[STATE_VALUES.index("pac_y")])] = pacbot 
        grid[int(state[STATE_VALUES.index("r_x")]), int(state[STATE_VALUES.index("r_y")])] = frightened_ghost if r_frightened else r_ghost
        grid[int(state[STATE_VALUES.index("p_x")]), int(state[STATE_VALUES.index("p_y")])] = frightened_ghost if p_frightened else p_ghost 
        grid[int(state[STATE_VALUES.index("o_x")]), int(state[STATE_VALUES.index("o_y")])] = frightened_ghost if o_frightened else o_ghost 
        grid[int(state[STATE_VALUES.index("b_x")]), int(state[STATE_VALUES.index("b_y")])] = frightened_ghost if b_frightened else b_ghost 
        
        # for row in grid:
        #     for cell in row:
        #         print(cell, end='')
        #     print()

        print(f'Mode: {state[STATE_VALUES.index("mode")]}, Lives: {state[STATE_VALUES.index("lives")]}, Cherry: {state[STATE_VALUES.index("cherry")]}, Frightened Timer: {state[STATE_VALUES.index("frightened_timer")]}')
        print(f'a - dir: {state[STATE_VALUES.index("pac_dir")]}')
        print(f'r - dir: {state[STATE_VALUES.index("r_dir")]}, frightened: {state[STATE_VALUES.index("r_frightened")]}, frightened_counter: {state[STATE_VALUES.index("r_frightened_counter")]}')
        print(f'p - dir: {state[STATE_VALUES.index("p_dir")]}, frightened: {state[STATE_VALUES.index("p_frightened")]}, frightened_counter: {state[STATE_VALUES.index("p_frightened_counter")]}')
        print(f'o - dir: {state[STATE_VALUES.index("o_dir")]}, frightened: {state[STATE_VALUES.index("o_frightened")]}, frightened_counter: {state[STATE_VALUES.index("o_frightened_counter")]}')
        print(f'b - dir: {state[STATE_VALUES.index("b_dir")]}, frightened: {state[STATE_VALUES.index("b_frightened")]}, frightened_counter: {state[STATE_VALUES.index("b_frightened_counter")]}')
        print(f'reward: {self.prev_reward}, done: {self.prev_done}')
        return grid
    
    def close(self):
        self.game_state = None

    @classmethod
    def get_grid_from_state(cls, state):

        STATE_VALUES = cls.STATE_VALUES
        
        pacbot = "a"
        r_ghost = "r"
        p_ghost = "p"
        o_ghost = "o"
        b_ghost = "b"
        wall = "#"
        pellet = "-"
        power_pellet = "%"

        grid = np.zeros((cls.GRID_HEIGHT, cls.GRID_WIDTH), dtype=str)
        grid[:, :] = ' '

        # fill in grid
        grid[cls.WALL_LOCATIONS != 0] = wall

        pellet_exists = state[np.array(STATE_VALUES) == "pellet"]
        for i in range(len(pellet_exists)):
            if pellet_exists[i]:
                grid[cls.PELLET_LOCATIONS == i+1] = pellet

        power_pellet_exists = state[np.array(STATE_VALUES) == "power_pellet"]
        for i in range(len(power_pellet_exists)):
            if power_pellet_exists[i]:
                grid[cls.POWER_PELLET_LOCATIONS == i+1] = power_pellet

        grid[int(state[STATE_VALUES.index("pac_x")]), int(state[STATE_VALUES.index("pac_y")])] = pacbot 
        grid[int(state[STATE_VALUES.index("r_x")]), int(state[STATE_VALUES.index("r_y")])] = r_ghost 
        grid[int(state[STATE_VALUES.index("p_x")]), int(state[STATE_VALUES.index("p_y")])] = p_ghost 
        grid[int(state[STATE_VALUES.index("o_x")]), int(state[STATE_VALUES.index("o_y")])] = o_ghost 
        grid[int(state[STATE_VALUES.index("b_x")]), int(state[STATE_VALUES.index("b_y")])] = b_ghost 

        return grid

class VisualPacBotEnv(PacBotEnv):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.observation_space = spaces.Box(low=0, high=1, shape=(12, self.GRID_HEIGHT, self.GRID_WIDTH), dtype=np.float32)

    """ 
    returns 12xgrid (
        pacman, 
        r, 
        p, 
        o, 
        b, 
        r_frightened, 
        p_frightened, 
        o_frightened, 
        b_frightened,
        pellets,
        power_pellets,
        walls,
    )
    """
    def _get_state(self):
        game_state = self.game_state

        state = np.zeros((12, self.GRID_HEIGHT, self.GRID_WIDTH))
        state[0, game_state.pacbot.pos[0], game_state.pacbot.pos[1]] = 1
        state[1, game_state.red.pos['current'][0], game_state.red.pos['current'][1]] = int(game_state.red.frightened_counter <= 0)
        state[2, game_state.pink.pos['current'][0], game_state.pink.pos['current'][1]] = int(game_state.pink.frightened_counter <= 0)
        state[3, game_state.orange.pos['current'][0], game_state.orange.pos['current'][1]] = int(game_state.orange.frightened_counter <= 0)
        state[4, game_state.blue.pos['current'][0], game_state.blue.pos['current'][1]] = int(game_state.blue.frightened_counter <= 0)
        state[5, game_state.red.pos['current'][0], game_state.red.pos['current'][1]] = game_state.red.frightened_counter / 40
        state[6, game_state.pink.pos['current'][0], game_state.pink.pos['current'][1]] = game_state.pink.frightened_counter / 40
        state[7, game_state.orange.pos['current'][0], game_state.orange.pos['current'][1]] = game_state.orange.frightened_counter / 40
        state[8, game_state.blue.pos['current'][0], game_state.blue.pos['current'][1]] = game_state.blue.frightened_counter / 40
        state[9] = 1*(np.array(game_state.grid) == o)
        state[10] = 1*(np.array(game_state.grid) == O)
        state[11] = 1*(np.array(game_state.grid) == I)

        return state 

    def render(self, mode='console'):
        if mode != 'console':
            raise NotImplementedError()

        state = self._get_state()
        
        pacbot = "a"
        r_ghost = "r"
        p_ghost = "p"
        o_ghost = "o"
        b_ghost = "b"
        r_ghost_frightened = "R"
        p_ghost_frightened = "P"
        o_ghost_frightened = "O"
        b_ghost_frightened = "B"
        wall = "#"
        pellet = "-"
        power_pellet = "%"

        grid = np.zeros((self.GRID_HEIGHT, self.GRID_WIDTH), dtype=str)
        grid[:, :] = ' '

        # fill in grid
        grid[state[11] != 0] = wall
        grid[state[9] != 0] = pellet
        grid[state[10] != 0] = power_pellet
        grid[state[0] != 0] = pacbot
        grid[state[1] != 0] = r_ghost
        grid[state[2] != 0] = p_ghost
        grid[state[3] != 0] = o_ghost
        grid[state[4] != 0] = b_ghost
        grid[state[5] != 0] = r_ghost_frightened
        grid[state[6] != 0] = p_ghost_frightened
        grid[state[7] != 0] = o_ghost_frightened
        grid[state[8] != 0] = b_ghost_frightened

        for row in grid:
            for cell in row:
                print(cell, end='')
            print()
            
            
        print(f'reward: {self.prev_reward}, done: {self.prev_done}')