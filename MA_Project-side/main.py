import numpy as np

import ql_agent
import env_pl_disc
import analysis_functions

import multiprocessing
import random
from multiprocessing import Manager

import time

##Define Parameters#

ALPHA = [0.1, 0.125, 0.15]
BETA = [2*(10 ** (-5)), (10 ** (-5)), 7*(10 ** (-6))]
Q = [99, 0]
DEV_ACTIONS = [0, 1, 2, 14]
MULTI_DEV_ACTIONS = [3]#0, 1, 2, 3]
DURATIONS = [1]#10, 25]
DEV_STRATS = [0, 1, 2, 3, 99]


DELTA = 0.95
NUM_PRICES = 15
NUM_OBS = NUM_PRICES ** 2

##Set the experiments you want to run to True
CONV = True
SINGLE = False
MULTI = False
PERMA = False

def run_session(session_id, env, alpha, beta, imp_res, exploit, dev_action, dev_duration, q_val, storage):

    ##determine whether q-matrices are to be initialized in Calvano style or not
    if q_val == 99:
        c_indic = True
    else:
        c_indic = False

    observations, infos = env.reset()
    agents = env.possible_agents

    ##initialize q_matrices
    ql_tables = {agent: ql_agent.QLAgent(env, alpha=alpha, beta=beta, delta=DELTA, q_init=q_val, c_init=c_indic)
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
                output = analysis_functions.explo_test(ql_tables, observations, states, actions, env, dev_action)
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




def main(alpha, beta, imp_res, exploit, dev_action, dev_duration, q_val, num_sessions):

    env = env_pl_disc.parallel_env(render_mode=None, num_prices=NUM_PRICES)

    with Manager() as manager:
        storage = manager.list()
        with multiprocessing.Pool(processes=num_sessions) as pool:
            pool.starmap(
                run_session,
                [(i, env, alpha, beta, imp_res, exploit, dev_action, dev_duration, q_val, storage) for i in range(num_sessions)],
            )

        results = np.vstack(storage)

    print("Experiment for alpha =", alpha, "beta =", beta, "imp_res = ", imp_res, "exploit =", exploit,
          "dev_action =", dev_action, "dev_duration =", dev_duration, "q_val =", q_val, "finished.")

    return results



if __name__ == "__main__":



    start_time = time.time()
   ####Convergence Experiment. looping through all alphas and betas and both types of q initializations
    if CONV:
        for a in ALPHA:
            for b in BETA:
                #for q in Q:
                data = main(alpha=a, beta=b, imp_res=False, exploit=False, dev_action=1, dev_duration= 1, q_val = 0, num_sessions=84)
                np.savetxt(f"results_conv/a_{a}_b_{b}_q_{0}_all.csv", data, delimiter=",", fmt='%d')

    ####One period price deviation experiment. Looping through betas and the durations of the deviation.
    if SINGLE:
        for b in BETA:
            for da in DEV_ACTIONS:
                data = main(alpha=0.125, beta=b, imp_res=True, exploit=False, dev_action=da, dev_duration = 1, q_val = 99, num_sessions=84)
                np.savetxt(f"results_imp_res_multi/b_{b}_dur_1_devact_{da}_all.csv", data, delimiter=",", fmt='%d')

    ####Multiple period price deviation experiment. Looping through betas and the durations of the deviation.
    if MULTI:
        for b in BETA:
            for du in DURATIONS:
                for da in MULTI_DEV_ACTIONS:
                    data = main(alpha=0.125, beta=b, imp_res=True, exploit=False, dev_action=da, dev_duration = du, q_val = 99, num_sessions=84)
                    np.savetxt(f"results_imp_res_multi/b_{b}_dur_{du}_devact_{da}_all.csv", data, delimiter=",", fmt='%d')

    ####Permanent deviation experiment. Looping through beta and the type of deviating strategy. (Either only 1 or [0,1,2] with equal probability)
    if PERMA:
        #for a in ALPHA:
        for b in BETA:
            for ds in DEV_STRATS:
                data = main(alpha=0.125, beta=b, imp_res=False, exploit=True, dev_action=ds, dev_duration= 1, q_val = 99, num_sessions=84)
                np.savetxt(f"results_perm_dev/a_{0.125}b_{b}_devstrat_{ds}_all.csv", data, delimiter=",", fmt='%d')

    # End the timer
    end_time = time.time()

    # Calculate the duration
    duration = end_time - start_time

    # Print the duration
    print(f"Simulation took {duration} seconds")

#End
#########################################







