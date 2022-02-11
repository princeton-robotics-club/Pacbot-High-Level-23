from gym_wrapper import PacBotEnv

if __name__ == "__main__":
    env = PacBotEnv(speed=1)
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
        _, _, done, _ = env.step(action)
        env.render()

        if done:
            env.reset()
            env.render()
        key = input()