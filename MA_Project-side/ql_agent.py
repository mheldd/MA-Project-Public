import numpy as np

class QLAgent:
    def __init__(
        self, env, alpha, beta, delta, q_init, c_init = False
    ):

        ##initialize the q-matrice using the dimensions of the observation and action space

        self.discount_factor = delta
        ##alpha
        self.learning_rate = alpha
        ##beta
        self.exploration_parameter = beta
        self.epsilon = 1
        self.action_space = env.action_space(self)
        self.observation_space = env.observation_space(self)
       #self.q_values = np.zeros((self.observation_space.n, self.action_space.n), dtype=np.float64)
        self.q_values = np.full((self.observation_space.n, self.action_space.n), fill_value= q_init, dtype=np.float64)
        self.num_moves = 0
        self.conv_count = 0
        self.converged = False
        self.conv_threshhold = 100000

        if c_init:
            ETA = 0.1
            PNASH = 1.47293
            PMONOP = 1.92498

            a1 = 2
            my = 1 / 4
            Cost = 1
            delta = 0.95


            LBOUND = PNASH - ETA * (PMONOP - PNASH)
            HBOUND = PMONOP + ETA * (PMONOP - PNASH)
            MOVESc = np.linspace(LBOUND, HBOUND, self.action_space.n)

            list = []

            for a in MOVESc:
                rewards = 0
                for b in MOVESc:
                    demand = (np.e ** ((a1 - a) / my)) / (
                            np.e ** ((a1 - a) / my) + np.e ** ((a1 - b) / my) + 1)
                    rewards += demand * (a - Cost)
                list.append((rewards / ((1 - delta) * self.action_space.n)))

            for i in range(self.action_space.n):
                self.q_values[:, i] = list[i]



        #print(self.q_values)


    ##function to either choose a random action or the best action based on the q-matrice depending on exploration
    def get_action(self, observation):
        self.num_moves += 1
        #print(self.action_space)
        if np.random.random() < self.epsilon:
            #('random action')
            return self.action_space.sample()
        else:
            #print(self.q_values[observation])
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
        ##save the action with the max q-value given the former observation before updating

        ##update the q-value corresponding to the former observation and the chosen action
        self.q_values[former_observation, action] = self.learning_rate*(reward + self.discount_factor*np.max(self.q_values[observation])) + (1-self.learning_rate)*self.q_values[former_observation, action]

        ##increase the convergence count if the optimal response has not changed after updating
        if action == int(np.argmax(self.q_values[former_observation])):
            #print(action)
            #print(int(np.argmax(self.q_values[former_observation])))
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
