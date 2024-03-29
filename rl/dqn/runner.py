import torch
import numpy as np
import gym
from torch.utils.tensorboard import SummaryWriter
from replay_buffer import *
from dqn import DQN
import argparse
import sys

sys.path.append("../../")
from simulator.gym_wrappers import PacBotEnv
from policies.high_level_policy import HighLevelPolicy


class Runner:
    def __init__(self, args, env_name, number, seed):
        self.args = args
        self.env_name = env_name
        self.number = number
        self.seed = seed

        self.env = PacBotEnv(log=False, normalized=True)  # gym.make(env_name)
        self.env_evaluate = PacBotEnv(log=False, normalized=True)
        # self.env_evaluate = gym.make(
        #     env_name
        # )  # When evaluating the policy, we need to rebuild an environment
        self.env.seed(seed)
        self.env.action_space.seed(seed)
        self.env_evaluate.seed(seed)
        self.env_evaluate.action_space.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        self.args.state_dim = self.env.observation_space.shape[0]
        self.args.action_dim = self.env.action_space.n
        self.args.episode_limit = (
            5000  # self.env._max_episode_steps  # Maximum number of steps per episode
        )
        print("env={}".format(self.env_name))
        print("state_dim={}".format(self.args.state_dim))
        print("action_dim={}".format(self.args.action_dim))
        print("episode_limit={}".format(self.args.episode_limit))

        if args.use_per and args.use_n_steps:
            self.replay_buffer = N_Steps_Prioritized_ReplayBuffer(args)
        elif args.use_per:
            self.replay_buffer = Prioritized_ReplayBuffer(args)
        elif args.use_n_steps:
            self.replay_buffer = N_Steps_ReplayBuffer(args)
        else:
            self.replay_buffer = ReplayBuffer(args)
        self.agent = DQN(args)

        self.algorithm = "DQN"
        if (
            args.use_double
            and args.use_dueling
            and args.use_noisy
            and args.use_per
            and args.use_n_steps
        ):
            self.algorithm = "Rainbow_" + self.algorithm
        else:
            if args.use_double:
                self.algorithm += "_Double"
            if args.use_dueling:
                self.algorithm += "_Dueling"
            if args.use_noisy:
                self.algorithm += "_Noisy"
            if args.use_per:
                self.algorithm += "_PER"
            if args.use_n_steps:
                self.algorithm += "_N_steps"

        self.writer = SummaryWriter(
            log_dir="runs/DQN/{}_env_{}_number_{}_seed_{}".format(
                self.algorithm, env_name, number, seed
            )
        )

        self.evaluate_num = 0  # Record the number of evaluations
        self.evaluate_rewards = []  # Record the rewards during the evaluating
        self.total_steps = 0  # Record the total steps during the training
        if args.use_noisy:  # 如果使用Noisy net，就不需要epsilon贪心策略了
            self.epsilon = 0
        else:
            self.epsilon = self.args.epsilon_init
            self.epsilon_min = self.args.epsilon_min
            self.epsilon_decay = (
                self.args.epsilon_init - self.args.epsilon_min
            ) / self.args.epsilon_decay_steps

        self.last_checkpoint_ind = 0

        self.teacher = HighLevelPolicy()
        self.pretrain = args.pretrain
        self.pretrain_steps = args.pretrain_steps

    def run(
        self,
    ):
        self.evaluate_policy()
        # TODO see if we should change this to an episodic approach
        while self.total_steps < self.args.max_train_steps:
            state = self.env.reset()
            done = False
            episode_steps = 0
            mask = self.env.generate_mask()
            while not done:
                if self.pretrain and self.total_steps < self.pretrain_steps:
                    action = self.teacher.get_action(
                        self.teacher.get_state(self.env, state)
                    )
                else:
                    action = self.agent.choose_action(state, mask, epsilon=self.epsilon)
                next_state, reward, done, extra = self.env.step(action)
                mask = extra["mask"]
                episode_steps += 1
                self.total_steps += 1

                if not self.args.use_noisy:  # Decay epsilon
                    self.epsilon = (
                        self.epsilon - self.epsilon_decay
                        if self.epsilon - self.epsilon_decay > self.epsilon_min
                        else self.epsilon_min
                    )

                # When dead or win or reaching the max_episode_steps, done will be True, we need to distinguish them;
                # terminal means dead or win, there is no next state s';
                # but when reaching the max_episode_steps,there is a next state s' actually.
                # TODO see if we can ignore episode limits
                # https://stackoverflow.com/questions/42787924/why-is-episode-done-after-200-time-steps-gym-environment-mountaincar
                if done and episode_steps != self.args.episode_limit:
                    # TODO see if we can remove this
                    if self.env_name == "LunarLander-v2":
                        if reward <= -100:
                            reward = -1  # good for LunarLander
                    terminal = True
                else:
                    terminal = False

                terminal = terminal or extra["life_lost"]

                self.replay_buffer.store_transition(
                    state, action, reward, next_state, terminal, done
                )  # Store the transition
                state = next_state

                if self.replay_buffer.current_size >= self.args.batch_size:
                    self.agent.learn(self.replay_buffer, self.total_steps)

                if self.total_steps % self.args.evaluate_freq == 0:
                    self.evaluate_policy()

        # Save reward
        np.save(
            "./data_train/{}_env_{}_number_{}_seed_{}.npy".format(
                self.algorithm, self.env_name, self.number, self.seed
            ),
            np.array(self.evaluate_rewards),
        )

    def evaluate_policy(
        self,
    ):
        evaluate_reward = 0
        total_score = 0
        high_score = float("-inf")
        low_score = float("inf")
        self.agent.net.eval()
        for _ in range(self.args.evaluate_times):
            state = self.env_evaluate.reset()
            done = False
            episode_reward = 0
            mask = self.env_evaluate.generate_mask()
            while not done:
                action = self.agent.choose_action(state, mask, epsilon=0)
                next_state, reward, done, extra = self.env_evaluate.step(action)
                mask = extra["eval_mask"]
                episode_reward += reward
                state = next_state
            score = self.env_evaluate.game_state.score
            total_score += score
            high_score = max(high_score, score)
            low_score = min(low_score, score)
            evaluate_reward += episode_reward
        self.agent.net.train()
        evaluate_reward /= self.args.evaluate_times
        if self.evaluate_rewards:
            if evaluate_reward > self.evaluate_rewards[self.last_checkpoint_ind] and (
                self.args.use_noisy or self.epsilon == self.epsilon_min
            ):
                self.last_checkpoint_ind = len(self.evaluate_rewards)
                self.agent.save_checkpoint(self.args.netid, self.algorithm)

        self.evaluate_rewards.append(evaluate_reward)
        print(
            "total_steps:{} \t evaluate_reward:{} \t epsilon：{}".format(
                self.total_steps, evaluate_reward, self.epsilon
            )
        )
        self.writer.add_scalar(
            "step_rewards_{}".format(self.env_name),
            evaluate_reward,
            global_step=self.total_steps,
        )
        self.writer.add_scalar(
            "average_game_score_{}".format(self.env_name),
            total_score / self.args.evaluate_times,
            self.total_steps,
        )
        self.writer.add_scalar(
            "high_game_score_{}".format(self.env_name), high_score, self.total_steps
        )
        self.writer.add_scalar(
            "low_game_score_{}".format(self.env_name), low_score, self.total_steps
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Hyperparameter Setting for DQN")
    parser.add_argument(
        "--max_train_steps",
        type=int,
        default=int(4e5),
        help=" Maximum number of training steps",
    )
    parser.add_argument(
        "--evaluate_freq",
        type=float,
        default=1e3,
        help="Evaluate the policy every 'evaluate_freq' steps",
    )
    parser.add_argument("--evaluate_times", type=int, default=3, help="Evaluate times")

    parser.add_argument(
        "--buffer_capacity",
        type=int,
        default=int(1e5),
        help="The maximum replay-buffer capacity ",
    )
    parser.add_argument("--batch_size", type=int, default=256, help="batch size")
    parser.add_argument(
        "--hidden_dim",
        type=int,
        default=256,
        help="The number of neurons in hidden layers of the neural network",
    )
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate of actor")
    parser.add_argument("--gamma", type=float, default=0.99, help="Discount factor")
    parser.add_argument(
        "--epsilon_init", type=float, default=0.5, help="Initial epsilon"
    )
    parser.add_argument(
        "--epsilon_min", type=float, default=0.1, help="Minimum epsilon"
    )
    parser.add_argument(
        "--epsilon_decay_steps",
        type=int,
        default=int(1e5),
        help="How many steps before the epsilon decays to the minimum",
    )
    parser.add_argument(
        "--tau", type=float, default=0.005, help="soft update the target network"
    )
    parser.add_argument(
        "--use_soft_update", type=bool, default=True, help="Whether to use soft update"
    )
    parser.add_argument(
        "--target_update_freq",
        type=int,
        default=200,
        help="Update frequency of the target network(hard update)",
    )
    parser.add_argument("--n_steps", type=int, default=5, help="n_steps")
    parser.add_argument("--alpha", type=float, default=0.6, help="PER parameter")
    parser.add_argument(
        "--beta_init",
        type=float,
        default=0.4,
        help="Important sampling parameter in PER",
    )
    parser.add_argument(
        "--use_lr_decay", type=bool, default=True, help="Learning rate Decay"
    )
    parser.add_argument("--grad_clip", type=float, default=10.0, help="Gradient clip")

    parser.add_argument(
        "--use_double", type=bool, default=True, help="Whether to use double Q-learning"
    )
    parser.add_argument(
        "--use_dueling", type=bool, default=True, help="Whether to use dueling network"
    )
    parser.add_argument(
        "--use_noisy", type=bool, default=True, help="Whether to use noisy network"
    )
    parser.add_argument("--use_per", type=bool, default=True, help="Whether to use PER")
    parser.add_argument(
        "--use_n_steps",
        type=bool,
        default=True,
        help="Whether to use n_steps Q-learning",
    )
    parser.add_argument(
        "--netid", type=str, required=True, help="Name for neural network checkpoints"
    )
    parser.add_argument("--pretrain", help="Pretrain model", action="store_true")
    parser.add_argument(
        "--pretrain_steps", type=int, default=int(5e4), help="Steps in pretraining"
    )

    args = parser.parse_args()

    # env_names = ["CartPole-v1", "LunarLander-v2"]
    # env_index = 1
    env_name = "PacBotEnv"
    for seed in [0, 10, 100]:
        runner = Runner(args=args, env_name=env_name, number=1, seed=seed)
        runner.run()
