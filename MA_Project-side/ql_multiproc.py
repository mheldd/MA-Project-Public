import ql_agent
import env_pl_disc
import multiprocessing
import random

#nash: 4.683105308334808
#average: 5.930776309195112
Tables = []
ALPHA = 0.125
##beta = 10^-5 is the midpoint of the grid. Kann mir ja den grid selbst computen und dann checken, wie ich das reasonable spacen kann.
BETA = (10**(-5))
DELTA = 0.95
Q_FILL_VALUE = 5.930776309195112
NUM_PRICES = 15
NUM_OBS = NUM_PRICES**2


def run_session(session_id, env, alpha, beta, imp_res, exploit):
    observations, infos = env.reset()
    agents = env.possible_agents

    ##initialize q_matrices
    ql_tables = {agent: ql_agent.QLAgent(env, alpha= alpha, beta= beta, delta= DELTA, q_init= Q_FILL_VALUE, c_init=True) for agent in agents}


    ##initalize actions outside action space. Will produce error if this is used.
    actions = {agent: 99 for agent in agents}
    ##the first state is chosen uniformly random out of all states
    states = {agent: random.randint(0, (NUM_OBS-1)) for agent in agents}

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
            if imp_res:
                impulse_response(ql_tables, observations, states, env)
                env.agents = []

            elif exploit:
                for agent in agents:
                    explo_test(ql_tables, agent, observations, states, env)
                env.agents = []

            else:
                #if i == 0:
                    #for agent in agents:
                        #Tables.append(ql_tables[agent].q_values)

                last_ten_actions.append(actions)

                for agent in agents:
                    last_ten_rewards[agent] += rewards[agent]
                i += 1
                if i >= 10:
                    for agent in agents:
                        last_ten_rewards[agent] = last_ten_rewards[agent]/10
                        print(ql_tables[agent].num_moves)
                        #print(ql_tables[agent].q_values, agent, session_id)
                    env.agents = []


    env.close()


    return f"Session {session_id} complete", last_ten_actions, last_ten_rewards, Tables


def impulse_response(ql_tables, observations, states, env):

    agents = env.possible_agents
    actions = {a: 99 for a in agents}
    deviator = random.randint(0,1)

    for i in range(50):
        if i == 0:
            actions[agents[deviator]] = 0
            actions[agents[1-deviator]] = ql_tables[agents[1-deviator]].get_action(observations[agents[1-deviator]])
        else:
            for agent in agents:
                actions[agent] = ql_tables[agent].get_action(observations[agent])

        print(actions)

        observations, rewards, termination, truncation, infos = env.step(actions)

        for agent in agents:
            ql_tables[agent].update(states[agent], observations[agent], actions[agent], rewards[agent], termination)

        states = observations


def explo_test(ql_tables, agent, observations, states, env):

    if agent == 'player_0':
        exploiter = 'player_1'

    else:
        exploiter = 'player_0'

    agents = env.possible_agents

    actions = {a: 99 for a in agents}
    tot_rewards = {a: 0 for a in agents}

    for i in range(100000):
        actions[agent] = ql_tables[agent].get_action(observations[agent])
        ql_tables[agent].decay_epsilon()
        actions[exploiter] = random.randint(0,2)
        print(actions)

        observations, rewards, termination, truncation, infos = env.step(actions)
        for a in agents:
            tot_rewards[a] += rewards[a]
        ql_tables[agent].update(states[agent], observations[agent], actions[agent], rewards[agent], termination)

        states = observations

    print('exploiter:', exploiter, tot_rewards)



def main(alpha = ALPHA, beta = BETA, imp_res = False, exploit = False):
    num_sessions = 12
    env = env_pl_disc.parallel_env(render_mode=None, num_prices= NUM_PRICES)

    with multiprocessing.Pool(processes=num_sessions) as pool:
        results = pool.starmap(
            run_session,
            [(i, env, alpha, beta, imp_res, exploit) for i in range(num_sessions)],
        )
        print(results)



if __name__ == "__main__":
    main()

    #exploitation_test(0, env_pl_disc.parallel_env(render_mode=None, num_prices= NUM_PRICES))



