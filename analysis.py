from pathlib import Path
import os
import glob
from simulator.gym_wrappers import PacBotEnv


class Analysis:
    def __init__(self, output_file: str) -> None:
        self.trials = 0
        self.total_score = 0
        self.worst_score = float("inf")
        self.best_score = float("-inf")
        self.shortest_run = float("inf")
        self.longest_run = float("-inf")
        self.wins = 0

        self.longest_calc_time = float("-inf")
        self.num_calcs = 0
        self.total_calc_time = 0

        self.pellets_remaining = 0
        self.worst_pellets_remaining = float("-inf")

        self.output_file = output_file if output_file else "output.txt"

        self.moves = []

        files = glob.glob(os.path.join("replay", "*"))
        for f in files:
            os.remove(f)

    def log_calc(self, elapsed_time):
        self.longest_calc_time = max(elapsed_time, self.longest_calc_time)
        self.num_calcs += 1
        self.total_calc_time += elapsed_time

    def log_endgame(self, env: PacBotEnv):
        self.trials += 1
        self.total_score += env.running_score
        self.worst_score = min(env.running_score, self.worst_score)
        self.best_score = max(env.running_score, self.best_score)
        self.shortest_run = min(env.ticks_passed, self.shortest_run)
        self.longest_run = max(env.ticks_passed, self.longest_run)
        if env.game_state._are_all_pellets_eaten():
            self.wins += 1
        else:
            self.pellets_remaining += env.game_state.pellets
            self.worst_pellets_remaining = max(
                self.worst_pellets_remaining, env.game_state.pellets
            )

    def write(self):
        filepath = os.path.join("output", self.output_file)
        Path("output").mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            f.write(f"Average score per run: {self.total_score / self.trials}\n")
            f.write(f"Number of trials: {self.trials}\n")
            f.write(f"Number of wins: {self.wins}\n")
            f.write(f"Range: {self.worst_score} - {self.best_score}\n")
            f.write(f"Longest Run: {self.longest_run} ticks\n")
            f.write(f"Shortest Run: {self.shortest_run} ticks\n")
            f.write(f"Num Calcs: {self.num_calcs}\n")
            f.write(f"Average Time: {self.total_calc_time / self.num_calcs}\n")
            f.write(f"Largest Time: {self.longest_calc_time}\n")
            if self.wins != self.trials:
                f.write(
                    f"Average Pellets Remaining (Losses): {self.pellets_remaining / (self.trials - self.wins)}\n"
                )
                f.write(f"Most Pellets Remaining: {self.worst_pellets_remaining}")

    def reset(self):
        self.moves = []

    def log_replay(self, env: PacBotEnv, state, just_died: bool):
        curr_move = []
        labels = ["pac", "r", "b", "o", "p"]
        for label in labels:
            curr_move.append(int(state[label][0]))
            curr_move.append(int(state[label][1]))
        curr_move.append(int(state["orientation"]))
        curr_move.append(int(state["rf"]))
        curr_move.append(int(state["bf"]))
        curr_move.append(int(state["of"]))
        curr_move.append(int(state["pf"]))
        curr_move.append(int(just_died))
        curr_move.append(env.game_state.state)
        curr_move.append(env.game_state.lives)
        self.moves.append(" ".join(str(move) for move in curr_move))

        # make new lines for pellet and power pellet locations
        self.moves.append(
            " ".join(f"{coord[0]} {coord[1]}" for coord in state["pellets"].tolist())
        )
        self.moves.append(
            " ".join(
                f"{coord[0]} {coord[1]}" for coord in state["power_pellets"].tolist()
            )
        )

    def write_replay(self, env: PacBotEnv):
        filepath = os.path.join("replay", "replay.txt")
        Path("replay").mkdir(parents=True, exist_ok=True)
        # contains score, time, and pellets remaining in that order
        metadata = [
            env.running_score,
            env.ticks_passed,
            env.game_state.pellets,
        ]
        with open(filepath, "w") as f:
            for metric in metadata:
                f.write(f"{metric}\n")
            f.writelines(move + "\n" for move in self.moves)
