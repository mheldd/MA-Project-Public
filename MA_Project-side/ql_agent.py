import numpy as np

class QLAgent:
    def __init__(
        self, env, alpha, beta, delta, q_init, c_init = False
    ):

        self.discount_factor = delta
        self.learning_rate = alpha
        self.exploration_parameter = beta
        self.epsilon = 1
        self.action_space = env.action_space(self)
        self.observation_space = env.observation_space(self)
        self.q_values = np.full((self.observation_space.n, self.action_space.n), fill_value= q_init, dtype=np.float64)
        self.num_moves = 0
        self.conv_count = 0
        self.converged = False
        self.conv_threshhold = 100000

        ##initalizing the q_values as in the Calvano 2020 paper.#
        if c_init:
            eta = 0.1
            pnash = 1.47293
            pmonop = 1.92498

            a1 = 2
            my = 1 / 4
            cost = 1
            delta = 0.95


            lbound = pnash - eta * (pmonop - pnash)
            hbound = pmonop + eta * (pmonop - pnash)
            movesc = np.linspace(lbound, hbound, self.action_space.n)

            it_list = []

            for a in movesc:
                rewards = 0
                for b in movesc:
                    demand = (np.e ** ((a1 - a) / my)) / (
                            np.e ** ((a1 - a) / my) + np.e ** ((a1 - b) / my) + 1)
                    rewards += demand * (a - cost)
                it_list.append((rewards / ((1 - delta) * self.action_space.n)))

            for i in range(self.action_space.n):
                self.q_values[:, i] = it_list[i]



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

        ##save best action given former observation to check for convergence below. This should be equal to action if the agent did not explore in a period.
        former_best_action = int(np.argmax(self.q_values[former_observation]))

        ##update the q-value corresponding to the former observation and the chosen action
        self.q_values[former_observation, action] = self.learning_rate*(reward + self.discount_factor*np.max(self.q_values[observation])) + (1-self.learning_rate)*self.q_values[former_observation, action]

        ##increase the convergence count if the optimal response has not changed after updating
        #if action == int(np.argmax(self.q_values[former_observation])):        ##old condition. Would also reset count if strategies are unchanged but another action is chosen due to exploration
        if former_best_action == int(np.argmax(self.q_values[former_observation])):
            self.conv_count += 1
        else:
            self.conv_count = 0
            self.converged = False

        #check for convergence
        if self.conv_count >= self.conv_threshhold:
            self.converged = True

    ##decay the exploration probability
    def decay_epsilon(self):
        self.epsilon = np.e**(-(self.exploration_parameter*self.num_moves))
