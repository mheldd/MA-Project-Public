import ql_agent
import env_pl_disc
import analysis_functions

import multiprocessing
import random

# nash: 4.683105308334808
# average: 5.930776309195112

ALPHA = 0.2
BETA = 7*(10 ** (-6))
DELTA = 0.95
Q_FILL_VALUE = 5.930776309195112
NUM_PRICES = 15
NUM_OBS = NUM_PRICES ** 2



def run_session(session_id, env, alpha, beta, imp_res, exploit, dev_action, random_strat):

    observations, infos = env.reset()
    agents = env.possible_agents

    ##initialize q_matrices
    ql_tables = {agent: ql_agent.QLAgent(env, alpha=alpha, beta=beta, delta=DELTA, q_init=Q_FILL_VALUE, c_init=True)
                 for agent in agents}

    ##initalize actions outside action space. Will produce error if this is used.
    actions = {agent: -1 for agent in agents}
    ##the first state is chosen uniformly random out of all states
    states = {agent: random.randint(0, (NUM_OBS - 1)) for agent in agents}



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

        if conv:
            if imp_res:
                analysis_functions.impulse_response(ql_tables, observations, states,actions , env, dev_action)
                env.agents = []

            elif exploit:
                analysis_functions.explo_test(ql_tables, observations, states, actions, env, random_strat)
                env.agents = []

            else:
                analysis_functions.conv_logging(ql_tables, observations, states, actions, env)
                env.agents = []

    env.close()


    return f"Session {session_id} complete"




def main(alpha=ALPHA, beta=BETA, imp_res=False, exploit=False, dev_action = 0, random_strat = False, num_sessions = 1):

    env = env_pl_disc.parallel_env(render_mode=None, num_prices=NUM_PRICES)

    with multiprocessing.Pool(processes=num_sessions) as pool:
        results = pool.starmap(
            run_session,
            [(i, env, alpha, beta, imp_res, exploit, dev_action, random_strat) for i in range(num_sessions)],
        )
        print(results)



if __name__ == "__main__":
    main(exploit = True, num_sessions = 3, random_strat = False)
    #print(np.load("actions_record.npy"))

    # exploitation_test(0, env_pl_disc.parallel_env(render_mode=None, num_prices= NUM_PRICES))



