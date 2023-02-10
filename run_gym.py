from simulator.gym_wrappers import PacBotEnv
from simulator.visualizer import Visualizer
import pygame

if __name__ == "__main__":
    visualizer = Visualizer()
    env = PacBotEnv(speed=1)
    obs = env.reset()
    grid = env.render()
    visualizer.draw_grid(grid)

    done = False
    key = visualizer.wait_manual_control()
    while key != pygame.K_q:
        action = 2
        if key == pygame.K_w:
            action = 0
        elif key == pygame.K_a:
            action = 1
        elif key == pygame.K_d:
            action = 3
        elif key == pygame.K_s:
            action = 4
        obs, reward, done, _ = env.step(action)
        grid = env.render()
        visualizer.draw_grid(grid)
        # for row in obs[11]:
        #     for cell in row:
        #         print('1' if cell else '0', end='')
        #     print()
        # print(reward, done)

        if done:
            env.reset()
            env.render()
        key = visualizer.wait_manual_control()