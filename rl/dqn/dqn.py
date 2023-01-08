import torch
import numpy as np
import copy
from network import Dueling_Net, Net
from replay_buffer import ReplayBuffer
import os
from pathlib import Path
import sys

sys.path.append("../")
from helpers import load_nnet, generate_mask


class DQN(object):
    def __init__(self, args):
        self.action_dim = args.action_dim
        self.batch_size = args.batch_size  # batch size
        self.max_train_steps = args.max_train_steps
        self.lr = args.lr  # learning rate
        self.gamma = args.gamma  # discount factor
        self.tau = args.tau  # Soft update
        self.use_soft_update = args.use_soft_update
        self.target_update_freq = args.target_update_freq  # hard update
        self.update_count = 0

        self.grad_clip = args.grad_clip
        self.use_lr_decay = args.use_lr_decay
        self.use_double = args.use_double
        self.use_dueling = args.use_dueling
        self.use_per = args.use_per
        self.use_n_steps = args.use_n_steps
        if self.use_n_steps:
            self.gamma = self.gamma**args.n_steps

        if self.use_dueling:  # Whether to use the 'dueling network'
            self.net = Dueling_Net(args)
        else:
            self.net = Net(args)

        self.target_net = copy.deepcopy(
            self.net
        )  # Copy the online_net to the target_net

        self.optimizer = torch.optim.Adam(self.net.parameters(), lr=self.lr)
        self.args = args

    def choose_action(self, state, mask, epsilon):
        if np.random.uniform() > epsilon:
            with torch.no_grad():
                state = torch.unsqueeze(torch.tensor(state, dtype=torch.float), 0)
                q: torch.Tensor = self.net(state)
                q = q.flatten().sub(q.min().item()) * torch.from_numpy(mask)
                action = q.argmax(dim=-1).item()
        else:
            action = np.random.choice(mask.nonzero()[0])
            # action = np.random.randint(0, self.action_dim)
        return action

    def learn(self, replay_buffer: ReplayBuffer, total_steps):
        batch, batch_index, IS_weight = replay_buffer.sample(total_steps)

        with torch.no_grad():  # q_target has no gradient
            if self.use_double:  # Whether to use the 'double q-learning'
                # Use online_net to select the action
                a_argmax = self.net(batch["next_state"]).argmax(
                    dim=-1, keepdim=True
                )  # shape：(batch_size,1)
                # Use target_net to estimate the q_target
                q_target = batch["reward"] + self.gamma * (
                    1 - batch["terminal"]
                ) * self.target_net(batch["next_state"]).gather(-1, a_argmax).squeeze(
                    -1
                )  # shape：(batch_size,)
            else:
                q_target = (
                    batch["reward"]
                    + self.gamma
                    * (1 - batch["terminal"])
                    * self.target_net(batch["next_state"]).max(dim=-1)[0]
                )  # shape：(batch_size,)

        q_current = (
            self.net(batch["state"]).gather(-1, batch["action"]).squeeze(-1)
        )  # shape：(batch_size,)
        td_errors = q_current - q_target  # shape：(batch_size,)

        # TODO could use different loss function
        if self.use_per:
            loss = (IS_weight * (td_errors**2)).mean()
            replay_buffer.update_batch_priorities(
                batch_index, td_errors.detach().numpy()
            )
        else:
            loss = (td_errors**2).mean()

        self.optimizer.zero_grad()
        loss.backward()
        if self.grad_clip:
            torch.nn.utils.clip_grad_norm_(self.net.parameters(), self.grad_clip)
        self.optimizer.step()

        # TODO figure out what this part means
        if self.use_soft_update:  # soft update
            for param, target_param in zip(
                self.net.parameters(), self.target_net.parameters()
            ):
                target_param.data.copy_(
                    self.tau * param.data + (1 - self.tau) * target_param.data
                )
        else:  # hard update
            self.update_count += 1
            if self.update_count % self.target_update_freq == 0:
                self.target_net.load_state_dict(self.net.state_dict())

        if self.use_lr_decay:  # learning rate Decay
            self.lr_decay(total_steps)

    def lr_decay(self, total_steps):
        lr_now = (
            0.9 * self.lr * (1 - total_steps / self.max_train_steps) + 0.1 * self.lr
        )
        for p in self.optimizer.param_groups:
            p["lr"] = lr_now

    def save_checkpoint(self, netid: str, algo_name: str):
        Path(f"checkpoints/{netid}").mkdir(parents=True, exist_ok=True)
        file_numbers = [
            int(f.split(".")[0].replace(f"{algo_name}_", ""))
            for f in os.listdir(os.path.join("checkpoints", netid))
            if algo_name in f
        ]
        last_ind = 0
        if file_numbers:
            last_ind = max(file_numbers)

        torch.save(
            {
                "model_state_dict": self.net.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "args": self.args,
            },
            os.path.join("checkpoints", netid, f"{algo_name}_{last_ind + 1}.pth"),
        )

    def load_checkpoint(self, filepath: str):
        load_nnet(filepath, self.net, self.optimizer)
