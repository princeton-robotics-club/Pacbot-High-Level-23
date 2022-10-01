# Princeton_Robotics_Club_PacBot

software for Princeton Robotics Club team in the 2022 Harvard PacBot competition

(make sure you have python installed if you want to run any of this code!)

Side note: Some of these instructions may only work on Windows. There are equivalent instructions for MacOS/Linux

To run the PacBot game code as a gym environment (which is the standard interface used in ML RL), first clone the repository to your computer with the following instructions. Using your terminal, navigate to your project directory and execute:

`git clone https://github.com/princeton-robotics-club/Pacbot-High-Level.git`

Optional: Activate a virtual environment. The purpose of this is to avoid installing packages globally and have the correct
versions of packages specific to your project. If you have multiple python projects on your computer, this is a godsend.
The following commands create a virtual environment called 'env' and activates it:

```
python -m venv env
env\Scripts\activate
```

Next, cd into the newly cloned git repository folder and install all package dependencies defined in requirements.txt:

`pip install -r requirements.txt`

A demo usage of the gym environment is in gym_simulator/gym_runner.py and can be run with (after you cd into gym_simulator):

`python run_high_level.py`

The demo takes input by keyboard input followed by an enter

q = quit

w = up

a = left

s = down

d = right

other = stay
