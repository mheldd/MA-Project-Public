import random

import ql_agent
import env_pl_disc

ALPHA = 0.1
BETA = 10**(-5)
DELTA = 0.95
Q_FILL_VALUE = 4.683105308334808
M = 15
env = env_pl_disc.parallel_env(render_mode = None, num_prices = 15)



if __name__ == "__main__":

    observations, infos = env.reset()
    agents = env.possible_agents

    ql_tables = {agent: ql_agent.QLAgent(env, alpha=ALPHA, beta=BETA, delta=DELTA, q_init=Q_FILL_VALUE) for agent in agents}


    states = {agent: random.randint(0, 225) for agent in agents}
    actions = {agent: None for agent in agents}
    last_ten_actions = []
    last_ten_rewards = {agent: 0 for agent in agents}
    i = 0
    conv = False

    while env.agents:

        for agent in agents:
            actions[agent] = ql_tables[agent].get_action(observations[agent])
            ql_tables[agent].decay_epsilon()

        observations, rewards, termination, truncation, infos = env.step(actions)

        for agent in agents:
            if ql_tables[agent].num_moves > 1:
                ql_tables[agent].update(states[agent], observations[agent], actions[agent], rewards[agent], termination)

        states = observations

        if all(ql_tables[agent].converged == True for agent in agents):
            conv = True

        if conv == True:
            last_ten_actions.append(actions)

            for agent in agents:
                last_ten_rewards[agent] += rewards[agent]
            i += 1
            if i >= 10:
                for agent in agents:
                    last_ten_rewards[agent] = last_ten_rewards[agent] / 10
                    print(ql_tables[agent].num_moves)
                env.agents = []

    env.close()