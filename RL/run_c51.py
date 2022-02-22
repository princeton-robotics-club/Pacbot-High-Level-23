# https://github.com/facebookresearch/torchbeast/blob/master/torchbeast/core/environment.py

import numpy as np
from collections import deque
import gym


class EpisodicLifeEnv(gym.Wrapper):
    def __init__(self, env):
        """Make end-of-life == end-of-episode, but only reset on true game over.
        Done by DeepMind for the DQN and co. since it helps value estimation.
        """
        gym.Wrapper.__init__(self, env)
        self.lives = 0
        self.was_real_done  = True

    def step(self, action):
        obs, reward, done, info = self.env.step(action)
        self.was_real_done = done
        # check current lives, make loss of life terminal,
        # then update lives to handle bonus lives
        lives = self.env.num_lives
        if lives < self.lives and lives > 0:
            # for Qbert sometimes we stay in lives == 0 condition for a few frames
            # so it's important to keep lives > 0, so that we only reset once
            # the environment advertises done.
            done = True
        self.lives = lives
        return obs, reward, done, info

    def reset(self, **kwargs):
        """Reset only when lives are exhausted.
        This way all states are still reachable even though lives are episodic,
        and the learner need not know about any of this behind-the-scenes.
        """
        if self.was_real_done:
            obs = self.env.reset(**kwargs)
        else:
            # no-op step to advance from terminal/lost life state
            obs, _, _, _ = self.env.step(0)
        self.lives = self.env.num_lives
        return obs

class ClipRewardEnv(gym.RewardWrapper):
    def __init__(self, env):
        gym.RewardWrapper.__init__(self, env)

    def reward(self, reward):
        """Bin reward to {+1, 0, -1} by its sign."""
        return np.sign(reward)

class DoubleStackEnv(gym.Wrapper):
    def __init__(self, env):
        gym.Wrapper.__init__(self, env)
        self.prevFrame = np.zeros(self.env.observation_space.shape)

    def step(self, action):
        obs, reward, done, info = self.env.step(action)
        prevFrame = self.prevFrame 
        self.prevFrame = obs
        return np.concatenate((obs, prevFrame), axis=0), reward, done, info

    def reset(self, **kwargs):
        self.prevFrame = np.zeros(self.env.observation_space.shape)
        return np.concatenate((self.env.reset(**kwargs), self.prevFrame), axis=0)

# Reference: https://arxiv.org/pdf/1707.06887.pdf
# https://github.com/ShangtongZhang/DeepRL/blob/master/deep_rl/agent/CategoricalDQN_agent.py

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.tensorboard import SummaryWriter

import argparse
from distutils.util import strtobool
import collections
import numpy as np
import gym
from gym.wrappers import TimeLimit, Monitor
from gym.spaces import Discrete, Box, MultiBinary, MultiDiscrete, Space
import time
import random
import os

from gym_simulator.gym_wrappers import VisualPacBotEnv

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='C51 agent')

    # PacBot arguments
    parser.add_argument('--env-speed', type=float, default=1,
                        help='the speed of the VisualPacBotEnv')

    # Common arguments
    parser.add_argument('--exp-name', type=str, default=os.path.basename(__file__).rstrip(".py"),
                        help='the name of this experiment')
    parser.add_argument('--learning-rate', type=float, default=1e-4,
                        help='the learning rate of the optimizer')
    parser.add_argument('--seed', type=int, default=2,
                        help='seed of the experiment')
    parser.add_argument('--total-timesteps', type=int, default=10000000,
                        help='total timesteps of the experiments')
    parser.add_argument('--torch-deterministic', type=lambda x:bool(strtobool(x)), default=True, nargs='?', const=True,
                        help='if toggled, `torch.backends.cudnn.deterministic=False`')
    parser.add_argument('--cuda', type=lambda x:bool(strtobool(x)), default=True, nargs='?', const=True,
                        help='if toggled, cuda will not be enabled by default')
    
    # Algorithm specific arguments
    parser.add_argument('--n-atoms', type=int, default=51,
                        help="the number of atoms")
    parser.add_argument('--v-min', type=float, default=-10,
                        help="the number of atoms")
    parser.add_argument('--v-max', type=float, default=10,
                        help="the number of atoms")
    parser.add_argument('--buffer-size', type=int, default=1000000,
                         help='the replay memory buffer size')
    parser.add_argument('--gamma', type=float, default=0.99,
                        help='the discount factor gamma')
    parser.add_argument('--target-network-frequency', type=int, default=1000,
                        help="the timesteps it takes to update the target network")
    parser.add_argument('--max-grad-norm', type=float, default=0.5,
                        help='the maximum norm for the gradient clipping')
    parser.add_argument('--batch-size', type=int, default=32,
                        help="the batch size of sample from the reply memory")
    parser.add_argument('--start-e', type=float, default=1.,
                        help="the starting epsilon for exploration")
    parser.add_argument('--end-e', type=float, default=0.01,
                        help="the ending epsilon for exploration")
    parser.add_argument('--exploration-fraction', type=float, default=0.10,
                        help="the fraction of `total-timesteps` it takes from start-e to go end-e")
    parser.add_argument('--learning-starts', type=int, default=80000,
                        help="timestep to start learning")
    parser.add_argument('--train-frequency', type=int, default=4,
                        help="the frequency of training")
    args = parser.parse_args()
    if not args.seed:
        args.seed = int(time.time())

# TRY NOT TO MODIFY: setup the environment
experiment_name = f"{args.exp_name}__{args.seed}__{int(time.time())}"
writer = SummaryWriter(f"runs/{experiment_name}")
writer.add_text('hyperparameters', "|param|value|\n|-|-|\n%s" % (
        '\n'.join([f"|{key}|{value}|" for key, value in vars(args).items()])))

# TRY NOT TO MODIFY: seeding
device = torch.device('cuda' if torch.cuda.is_available() and args.cuda else 'cpu')
env = VisualPacBotEnv(speed=args.env_speed)
env = gym.wrappers.RecordEpisodeStatistics(env) # records episode reward in `info['episode']['r']`
env = EpisodicLifeEnv(env)
env = ClipRewardEnv(env)
env = DoubleStackEnv(env)
random.seed(args.seed)
np.random.seed(args.seed)
torch.manual_seed(args.seed)
torch.backends.cudnn.deterministic = args.torch_deterministic
env.seed(args.seed)
env.action_space.seed(args.seed)
env.observation_space.seed(args.seed)
# respect the default timelimit
assert isinstance(env.action_space, Discrete), "only discrete action space is supported"

# modified from https://github.com/seungeunrho/minimalRL/blob/master/dqn.py#
class ReplayBuffer():
    def __init__(self, buffer_limit):
        self.buffer = collections.deque(maxlen=buffer_limit)
    
    def put(self, transition):
        self.buffer.append(transition)
    
    def sample(self, n):
        mini_batch = random.sample(self.buffer, n)
        s_lst, a_lst, r_lst, s_prime_lst, done_mask_lst = [], [], [], [], []
        
        for transition in mini_batch:
            s, a, r, s_prime, done_mask = transition
            s_lst.append(s)
            a_lst.append(a)
            r_lst.append(r)
            s_prime_lst.append(s_prime)
            done_mask_lst.append(done_mask)

        return np.array(s_lst), np.array(a_lst), \
               np.array(r_lst), np.array(s_prime_lst), \
               np.array(done_mask_lst)

# ALGO LOGIC: initialize agent here:
class Scale(nn.Module):
    def __init__(self, scale):
        super().__init__()
        self.scale = scale

    def forward(self, x):
        return x * self.scale
class QNetwork(nn.Module):
    def __init__(self, env, device, frames=24, n_atoms=51, v_min=-10, v_max=10):
        super(QNetwork, self).__init__()
        self.n_atoms = n_atoms
        self.atoms = torch.linspace(v_min, v_max, steps=n_atoms).to(device)
        self.network = nn.Sequential(
            Scale(1/255),
            nn.Conv2d(frames, 32, 3, stride=2),
            nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, stride=1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(6336, 512),
            nn.ReLU(),
            nn.Linear(512, env.action_space.n * n_atoms)
        )

    def forward(self, x, device):
        x = torch.Tensor(x).to(device)
        return self.network(x)

    def get_action(self, env, device, x,action=None):
        logits = self.forward(x, device)
        # probability mass function for each action
        pmfs = torch.softmax(logits.view(len(x), env.action_space.n, self.n_atoms), dim=2)
        q_values = (pmfs*self.atoms).sum(2)
        if action is None:
            action = torch.argmax(q_values, 1)
        return action, pmfs[torch.arange(len(x)), action]

def linear_schedule(start_e: float, end_e: float, duration: int, t: int):
    slope =  (end_e - start_e) / duration
    return max(slope * t + start_e, end_e)

rb = ReplayBuffer(args.buffer_size)
q_network = QNetwork(env, device, n_atoms=args.n_atoms, v_min=args.v_min, v_max=args.v_max).to(device)
target_network = QNetwork(env, device, n_atoms=args.n_atoms, v_min=args.v_min, v_max=args.v_max).to(device)
target_network.load_state_dict(q_network.state_dict())
optimizer = optim.Adam(q_network.parameters(), lr=args.learning_rate, eps=0.01/args.batch_size)
loss_fn = nn.MSELoss()
print(device.__repr__())
print(q_network)

# TRY NOT TO MODIFY: start the game
obs = env.reset()
episode_reward = 0
for global_step in range(args.total_timesteps):
    # ALGO LOGIC: put action logic here
    epsilon = linear_schedule(args.start_e, args.end_e, args.exploration_fraction*args.total_timesteps, global_step)
    if random.random() < epsilon:
        action = env.action_space.sample()
    else:
        action, pmf = target_network.get_action(env, device, obs.reshape((1,)+obs.shape))
        action = action.tolist()[0]

    # TRY NOT TO MODIFY: execute the game and log data.
    next_obs, reward, done, info = env.step(action)
    episode_reward += reward

    # TRY NOT TO MODIFY: record rewards for plotting purposes
    if 'episode' in info.keys():
        print(f"global_step={global_step}, episode_reward={info['episode']['r']}")
        writer.add_scalar("charts/episodic_return", info['episode']['r'], global_step)
        writer.add_scalar("charts/epsilon", epsilon, global_step)

    # ALGO LOGIC: training.
    rb.put((obs, action, reward, next_obs, done))
    if global_step > args.learning_starts and global_step % args.train_frequency == 0:
        s_obs, s_actions, s_rewards, s_next_obses, s_dones = rb.sample(args.batch_size)
        with torch.no_grad():
            _, next_pmfs = q_network.get_action(env, device, s_next_obses)
            next_atoms = torch.Tensor(s_rewards).to(device).unsqueeze(-1) + args.gamma * q_network.atoms  * (1 - torch.Tensor(s_dones).to(device).unsqueeze(-1))
            # projection
            delta_z = q_network.atoms[1]-q_network.atoms[0]
            tz = next_atoms.clamp(args.v_min, args.v_max)
            
            b = (tz - args.v_min)/ delta_z
            l = b.floor().clamp(0, args.n_atoms-1)
            u = b.ceil().clamp(0, args.n_atoms-1)
            # (l == u).float() handles the case where bj is exactly an integer
            # example bj = 1, then the upper ceiling should be uj= 2, and lj= 1
            d_m_l = (u + (l == u).float() - b) * next_pmfs
            d_m_u = (b - l) * next_pmfs
            target_pmfs = torch.zeros_like(next_pmfs)
            for i in range(target_pmfs.size(0)):
                target_pmfs[i].index_add_(0, l[i].long(), d_m_l[i])
                target_pmfs[i].index_add_(0, u[i].long(), d_m_u[i])
        
        _, old_pmfs = q_network.get_action(env, device, s_obs, s_actions)
        loss = (-(target_pmfs * old_pmfs.clamp(min=1e-5).log()).sum(-1)).mean()
        # loss = (target_pmfs * (target_pmfs.clamp(min=1e-5).log() - old_pmfs.clamp(min=1e-5).log())).sum(-1).mean()
        
        if global_step % 100 == 0:
            writer.add_scalar("losses/td_loss", loss, global_step)

        # optimize the midel
        optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(list(q_network.parameters()), args.max_grad_norm)
        optimizer.step()

        # update the target network
        if global_step % args.target_network_frequency == 0:
            target_network.load_state_dict(q_network.state_dict())

    # TRY NOT TO MODIFY: CRUCIAL step easy to overlook
    obs = next_obs
    if done:
        # important to note that because `EpisodicLifeEnv` wrapper is applied,
        # the real episode reward is actually the sum of episode reward of 5 lives
        # which we record through `info['episode']['r']` provided by gym.wrappers.RecordEpisodeStatistics
        obs, episode_reward = env.reset(), 0

env.close()
writer.close()
