import functools
import itertools
import numpy as np

from gymnasium.spaces import Discrete
from pettingzoo import ParallelEnv


NUM_ITERS = 1000000

LIST = []

lbound = 1.5
hbound = 2

NUM_AGENTS = 2
##Mapping played actions to rewards
NUM_PRICES = 5
MOVES = list(range(NUM_PRICES))
OBSERVATIONS = list(itertools.product(MOVES, repeat=NUM_AGENTS))

MOVESc = np.linspace(lbound, hbound, NUM_PRICES)

A = 2
MY = 1/4
Cost = 1

NONE = 0



class parallel_env(ParallelEnv):

    metadata = {"render_modes": ["human"], "name": "dp_env_pl_2"}

    def __init__(self, render_mode=None):
        self.possible_agents = ["player_" + str(r) for r in range(NUM_AGENTS)]

        # optional: a mapping between agent name and ID
        self.agent_name_mapping = dict(
            zip(self.possible_agents, list(range(len(self.possible_agents))))
        )
        self.render_mode = render_mode
        #self.steps = 0
        self.a = 2
        self.my = 1 / 4
        self.observation_mapping = {comb: idx for idx, comb in enumerate(OBSERVATIONS)}

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return Discrete(len(OBSERVATIONS)+1)

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return Discrete(NUM_PRICES)

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
        observations = {agent: NONE for agent in self.agents}
        self.state = observations

        return observations, infos

    def step(self, actions):

        rewards = {agent: 0.0 for agent in self.agents}
        if not actions:
            self.agents = []
            return {}, {}, {}, {}, {}

        actions_c = {agent: MOVESc[actions[agent]] for agent in self.agents}
        # rewards for all agents are placed in the rewards dictionary to be returned

        for agent in self.agents:
            pi = actions_c[agent]
            pj = actions_c[self.agents[1 - self.agent_name_mapping[agent]]]
            demand = (np.e ** ((self.a - pi) / self.my)) / (
                        np.e ** ((self.a - pi) / self.my) + np.e ** ((self.a - pj) / self.my))
            rewards[agent] = demand * (pi - Cost)
            # print("pi:", pi, "pj:", pj, "demand:", demand, "reward:", rewards[agent], "actions:", actions, "actions:", actions_c)

        observations = {agent: self.observation_mapping[(actions[agent], actions[self.agents[1 - self.agent_name_mapping[agent]]])] for agent in self.agents}

        terminations = {agent: False for agent in self.agents}
        truncations = {agent: False for agent in self.agents}
        infos = {agent: {} for agent in self.agents}

        self.num_moves += 1
        if self.num_moves >= NUM_ITERS:
            self.agents = []

        if self.render_mode == "human":
            self.render()

        return observations, rewards, terminations, truncations, infos