import ql_agent
import env_pl_disc
import multiprocessing
import random

#nash: 4.683105308334808
#average: 5.930776309195112

ALPHA = 0.15
BETA = (10**(-4))
DELTA = 0.95
Q_FILL_VALUE = 0
NUM_PRICES = 2
NUM_OBS = NUM_PRICES**2

def run_session(session_id, env):
    observations, infos = env.reset()
    agents = env.possible_agents

    ##initialize q_matrices
    ql_tables = {agent: ql_agent.QLAgent(env, alpha= ALPHA, beta= BETA, delta= DELTA, q_init= Q_FILL_VALUE, c_init=False) for agent in agents}


    ##initalize actions outside action space. Will produce error if this is used.
    actions = {agent: 99 for agent in agents}
    ##the first state is chosen uniformly random out of all states
    states = {agent: random.randint(0, NUM_OBS-1) for agent in agents}

    ##preparations for logging upon convergence
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
                    last_ten_rewards[agent] = last_ten_rewards[agent]/10
                    print(ql_tables[agent].num_moves)
                    print(ql_tables[agent].q_values, agent, session_id)
                env.agents = []


    env.close()


    return f"Session {session_id} complete", last_ten_actions, last_ten_rewards

def main():
    num_sessions = 6
    env = env_pl_disc.parallel_env(render_mode=None, num_prices= NUM_PRICES)

    with multiprocessing.Pool(processes=num_sessions) as pool:
        results = pool.starmap(
            run_session,
            [(i, env) for i in range(num_sessions)],
        )
        print(results)



if __name__ == "__main__":
    main()



