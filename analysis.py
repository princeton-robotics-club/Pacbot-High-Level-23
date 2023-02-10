from pathlib import Path
import os
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

        self.output_file = output_file if output_file else "output.txt"

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
