import numpy as np

import ql_agent
import env_pl_disc
import analysis_functions

import multiprocessing
import random
from multiprocessing import Manager

# nash: 4.683105308334808
# average: 5.930776309195112

ALPHA = [0.1, 0.125]#, 0.15]
#BETA = [2*(10 ** (-5)), 10 ** (-5), 7*(10 ** (-6))]
BETA = [10**(-3), 2*(10**(-5))]
DELTA = 0.95
Q_FILL_VALUE = 5.930776309195112
NUM_PRICES = 15
NUM_OBS = NUM_PRICES ** 2



def run_session(session_id, env, alpha, beta, imp_res, exploit, dev_action, dev_duration, random_strat, storage):

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
                output = analysis_functions.impulse_response(ql_tables, observations, states, actions, env, dev_action, dev_duration)
                env.agents = []

            elif exploit:
                output = analysis_functions.explo_test(ql_tables, observations, states, actions, env, dev_action, random_strat)
                env.agents = []

            else:
                output = analysis_functions.conv_logging(ql_tables, observations, states, actions, env)
                env.agents = []


            info_id = np.full((output.shape[0], 1), session_id)
            info_moves = np.full((output.shape[0], 1), env.num_moves)
            result = np.hstack((output, info_id, info_moves))
            storage.append(result)

    env.close()


    return f"Session {session_id} complete"




def main(alpha, beta, imp_res, exploit, dev_action, dev_duration, random_strat, num_sessions):

    env = env_pl_disc.parallel_env(render_mode=None, num_prices=NUM_PRICES)

    with Manager() as manager:
        storage = manager.list()
        with multiprocessing.Pool(processes=num_sessions) as pool:
            pool.starmap(
                run_session,
                [(i, env, alpha, beta, imp_res, exploit, dev_action, dev_duration, random_strat, storage) for i in range(num_sessions)],
            )

        results = np.vstack(storage)

    return results



if __name__ == "__main__":

    #data = main(alpha=0.125, beta=2*(10 ** (-5)), imp_res=False, exploit=False, dev_action = 0, random_strat = False, num_sessions = 6)
    #print(data)

    #basic looping through parameters
    #for a in ALPHA:
        #for b in BETA:
            #data = main(alpha=a, beta=b, imp_res=False, exploit=False, dev_action=0, random_strat=False, num_sessions=2)
            #np.savetxt(f"results_A/a_{a}_b_{b}_all.csv", data, delimiter=",")

    #create pilot data for each experiment
    a = 0.125
    b = 2*(10**(-5))

    ##convergence
    #data = main(alpha=a, beta=b, imp_res=False, exploit=False, dev_action=1, dev_duration= 1, random_strat=False, num_sessions=2)
    #np.savetxt(f"results_conv/a_{a}_b_{b}_all.csv", data, delimiter=",", fmt='%d')

    ##impulse response
    data = main(alpha=a, beta=b, imp_res=True, exploit=False, dev_action=1, dev_duration = 5, random_strat=False, num_sessions=2)
    np.savetxt(f"results_imp_res/a_{a}_b_{b}_all.csv", data, delimiter=",", fmt='%d')

    ##permanent deviation
    #data = main(alpha=a, beta=b, imp_res=False, exploit=True, dev_action=1, dev_duration= 1, random_strat=False, num_sessions=2)
    #np.savetxt(f"results_perm_dev/a_{a}_b_{b}_all.csv", data, delimiter=",", fmt='%d')







