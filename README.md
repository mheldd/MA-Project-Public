This repository contains code for simulations and data analyses that I carried out as part of my Master´s Thesis on algorithmic collusion.

The simulation code consists of 4 connected .py files. NumPy and PettingZoo are required.

main.py is the main file which is to be executed to run the simulations. Most of the relevant parameters (alpha, beta, delta, number of prices, ....) are set there. One can determine the types of experiments that should be run (temporary impulse response, permanent impulse response, regular convergence) by setting boolean variables to true. Multiprocessing of sessions is used to increase speed. The results are printed to the project´s folder as .csv files after the simulations have finished.

analysis_functions.py contains the specific functions that track the algorithms' behavior after convergence.

env_pl.py defines the economic environment using the PettingZoo framework.

ql_agent.py defines the QLAgent class which contains the Q-learning logic that is used by the algorithms to learn the environment.
