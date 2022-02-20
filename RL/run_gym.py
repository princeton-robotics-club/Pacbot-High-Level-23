from gym_simulator.gym_wrappers import VisualPacBotEnv

if __name__ == "__main__":
    env = VisualPacBotEnv(speed=1)
    obs = env.reset()
    env.render()

    done = False
    key = input()
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
        obs, reward, done, _ = env.step(action)
        env.render()
        # for row in obs[11]:
        #     for cell in row:
        #         print('1' if cell else '0', end='')
        #     print()
        # print(reward, done)

        if done:
            env.reset()
            env.render()
        key = input()