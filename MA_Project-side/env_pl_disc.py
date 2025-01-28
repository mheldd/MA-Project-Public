import functools
import itertools
import numpy as np

from gymnasium.spaces import Discrete
from pettingzoo import ParallelEnv


NUM_ITERS = 1000000000

ETA = 0.1

PNASH = 1.47293
PMONOP = 1.92498

LBOUND = PNASH - ETA*(PMONOP - PNASH)
HBOUND = PMONOP + ETA*(PMONOP - PNASH)

NUM_AGENTS = 2
NUM_PRICES = 15

class parallel_env(ParallelEnv):

    metadata = {"render_modes": ["human"], "name": "dp_env_pl_2"}

    def __init__(self, render_mode=None, num_prices = NUM_PRICES):
        self.possible_agents = ["player_" + str(r) for r in range(NUM_AGENTS)]
        self.agent_name_mapping = dict(
            zip(self.possible_agents, list(range(len(self.possible_agents))))
        )
        self.render_mode = render_mode
        self.num_moves = 0
        self.a = 2
        self.my = 1 / 4
        self.c = 1
        self.num_prices = num_prices
        self.observations = list(itertools.product(list(range(num_prices)), repeat=NUM_AGENTS))
        self.movesc = np.linspace(LBOUND, HBOUND, num_prices)
        self.observation_mapping = {comb: idx for idx, comb in enumerate(self.observations)}

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return Discrete(len(self.observations))

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return Discrete(self.num_prices)

    def render(self):
        pass

    def close(self):
        pass

    def reset(self, seed=None, options=None):

        self.agents = self.possible_agents[:]
        self.num_moves = 0
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        infos = {agent: {} for agent in self.agents}
        observations = {agent: 0 for agent in self.agents}

        return observations, infos

    def step(self, actions):

        rewards = {agent: 0.0 for agent in self.agents}
        if not actions:
            self.agents = []
            return {}, {}, {}, {}, {}

        actions_c = {agent: self.movesc[actions[agent]] for agent in self.agents}
        # rewards for all agents are placed in the rewards dictionary to be returned

        for agent in self.agents:
            pi = actions_c[agent]
            pj = actions_c[self.agents[1 - self.agent_name_mapping[agent]]]
            demand = (np.e ** ((self.a - pi) / self.my)) / (
                        np.e ** ((self.a - pi) / self.my) + np.e ** ((self.a - pj) / self.my)+1)
            rewards[agent] = float(demand * (pi - self.c))

        observations = {agent: self.observation_mapping[(actions[agent], actions[self.agents[1 - self.agent_name_mapping[agent]]])] for agent in self.agents}

        terminations = {agent: False for agent in self.agents}
        truncations = {agent: False for agent in self.agents}
        infos = {agent: {} for agent in self.agents}

        self.num_moves += 1

        if self.num_moves >= NUM_ITERS:
            self.agents = []


        return observations, rewards, terminations, truncations, infos