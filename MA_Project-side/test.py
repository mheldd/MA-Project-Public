import ql_agent
import env_pl_disc
import multiprocessing
import random
import numpy as np

# nash: 4.683105308334808
# average: 5.930776309195112
Tables = []
ALPHA = 0.125
BETA = 2*(10 ** (-5))
DELTA = 0.95
Q_FILL_VALUE = 5.930776309195112
NUM_PRICES = 15
NUM_OBS = NUM_PRICES ** 2



def run_session(session_id, env, alpha, beta, imp_res, exploit):

    observations, infos = env.reset()
    agents = env.possible_agents

    ##initialize q_matrices
    ql_tables = {agent: ql_agent.QLAgent(env, alpha=alpha, beta=beta, delta=DELTA, q_init=Q_FILL_VALUE, c_init=True)
                 for agent in agents}

    ##initalize actions outside action space. Will produce error if this is used.
    actions = {agent: 99 for agent in agents}
    ##the first state is chosen uniformly random out of all states
    states = {agent: random.randint(0, (NUM_OBS - 1)) for agent in agents}

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
                conv_logging(ql_tables, observations, states, actions, env)
                env.agents = []

    env.close()


    return f"Session {session_id} complete", last_ten_actions, last_ten_rewards, Tables


##Function to save the actions and profits of agents upon convergence (for table 1). Gets called when a session is converged.
def conv_logging(ql_tables, observations, states, actions, env):
    check_duration = 10
    record = np.zeros((check_duration, 4), dtype=np.float32)
    agents = env.possible_agents
    actions = actions
    for i in range(0, check_duration):
        for agent in agents:
            actions[agent] = ql_tables[agent].get_action(observations[agent])
            ql_tables[agent].decay_epsilon()

        observations, rewards, termination, truncation, infos = env.step(actions)

        #save actions of agents to column 0 and 1 and rewards to column 2 and 3
        for agent in agents:
            record[i, env.agent_name_mapping[agent]] = actions[agent] if actions[agent] is not None else -1
            record[i, env.agent_name_mapping[agent]+2] = rewards[agent] if rewards[agent] is not None else -1

            ql_tables[agent].update(states[agent], observations[agent], actions[agent], rewards[agent], termination)

        states = observations

    print(env.num_moves)
    print(record)


##Function for the impulse response analysis. Gets called when a session is converged.
def impulse_response(ql_tables, observations, states, env):

    ##record_size = 500000
    #actions_record = np.zeros((record_size, 2), dtype=np.int8)
    #if env.num_moves >= record_size - 1:
        #record_size *= 2
        #actions_record = np.resize(actions_record, (record_size, 2))
    #actions_record[env.num_moves, env.agent_name_mapping[agent]] = actions[agent] if actions[agent] is not None else -1
    #np.save("actions_record.npy", actions_record)

    agents = env.possible_agents
    actions = {a: 99 for a in agents}
    deviator = random.randint(0, 1)

    for i in range(50):
        if i == 0:
            actions[agents[deviator]] = 0
            actions[agents[1 - deviator]] = ql_tables[agents[1 - deviator]].get_action(
                observations[agents[1 - deviator]])
        else:
            for agent in agents:
                actions[agent] = ql_tables[agent].get_action(observations[agent])

        print(actions)

        observations, rewards, termination, truncation, infos = env.step(actions)

        for agent in agents:
            ql_tables[agent].update(states[agent], observations[agent], actions[agent], rewards[agent], termination)

        states = observations

#Function for the exploitation analysis. Gets called when a session is converged.
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
        actions[exploiter] = random.randint(0, 2)
        print(actions)

        observations, rewards, termination, truncation, infos = env.step(actions)
        for a in agents:
            tot_rewards[a] += rewards[a]
        ql_tables[agent].update(states[agent], observations[agent], actions[agent], rewards[agent], termination)

        states = observations

    print('exploiter:', exploiter, tot_rewards)


def main(alpha=ALPHA, beta=BETA, imp_res=False, exploit=False):
    num_sessions = 6
    env = env_pl_disc.parallel_env(render_mode=None, num_prices=NUM_PRICES)

    with multiprocessing.Pool(processes=num_sessions) as pool:
        results = pool.starmap(
            run_session,
            [(i, env, alpha, beta, imp_res, exploit) for i in range(num_sessions)],
        )
        print(results)


if __name__ == "__main__":
    main()
    #print(np.load("actions_record.npy"))

    # exploitation_test(0, env_pl_disc.parallel_env(render_mode=None, num_prices= NUM_PRICES))



