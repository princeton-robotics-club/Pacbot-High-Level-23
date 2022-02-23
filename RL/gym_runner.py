from gym_simulator.gym_wrapper import PacBotEnv
from gym_simulator.visualizer import Visualizer

if __name__ == "__main__":
    visualizer = Visualizer()
    env = PacBotEnv(visualizer, speed=1)
    obs = env.reset()
    env.render()

    done = False
    key = visualizer.wait()
    while key != "q":
        action = 2
        if key == "w":
            action = 0
        elif key == "a":
            action = 1
        elif key == "d":
            action = 3
        elif key == "s":
            action = 4
        obs, _, done, _ = env.step(action)
        env.render()
        #visualizer.draw_grid(env.get_grid_from_state(obs[0]))
        if done:
            env.reset()
            env.render()
        key = visualizer.wait()