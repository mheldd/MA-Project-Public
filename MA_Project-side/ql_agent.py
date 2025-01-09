import numpy as np

class QLAgent:
    def __init__(
        self, env
    ):

        ##initialize the q-matrice using the dimensions of the obsrvation and action space

        self.discount_factor = 0.95
        ##alpha
        self.learning_rate = 0.15
        ##beta
        self.exploration_parameter = 10**(-4)
        self.epsilon = 1
        self.action_space = env.action_space(self)
        self.observation_space = env.observation_space(self)
        self.q_values = np.zeros((self.observation_space.n, self.action_space.n), dtype=np.float64)
        self.num_moves = 0



    ##function to either choose a random action or the best action based on the q-matrice depending on exploration
    def get_action(self, observation):
        self.num_moves += 1
        if np.random.random() < self.epsilon:
            return self.action_space.sample()
        else:
            return int(np.argmax(self.q_values[observation]))



    ###function that updates the q-matrice before choosing a new action
    def update(
        self,
        former_observation: int,
        observation: int,
        action: int,
        reward: float,
        terminated: bool,
    ):
        """Updates the Q-value of an action."""
        future_q_value = (not terminated) * np.max(self.q_values[observation])
        temporal_difference = (
            reward + self.discount_factor * future_q_value - self.q_values[former_observation, action]
        )
        self.q_values[former_observation, action] += temporal_difference * self.learning_rate


    def decay_epsilon(self):
        self.epsilon = np.e**(-(self.exploration_parameter*self.num_moves))
