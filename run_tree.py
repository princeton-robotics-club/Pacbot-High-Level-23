from simulator.tree_wrappers import PacBotNode
from simulator.visualizer import Visualizer

if __name__ == "__main__":
    visualizer = Visualizer()
    node = PacBotNode(speed=1)

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
        node = node.next_node(action)
        grid = node.env.render()
        visualizer.draw_grid(grid)
        # for row in obs[11]:
        #     for cell in row:
        #         print('1' if cell else '0', end='')
        #     print()
        # print(reward, done)

        if done:
            node = PacBotNode(speed=1)
        key = visualizer.wait()