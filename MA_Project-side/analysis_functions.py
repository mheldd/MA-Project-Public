import numpy as np
import random


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
def impulse_response(ql_tables, observations, states, actions, env, dev_action):

    agents = env.possible_agents
    actions = actions
    deviator = random.randint(0, 1)

    check_duration = 15
    record = np.zeros((check_duration, 2), dtype=np.float32)

    for i in range(0, check_duration):
        if i == 2:
            actions[agents[deviator]] = dev_action
            actions[agents[1 - deviator]] = ql_tables[agents[1 - deviator]].get_action(
                observations[agents[1 - deviator]])
        else:
            for agent in agents:
                actions[agent] = ql_tables[agent].get_action(observations[agent])

        print(actions)

        observations, rewards, termination, truncation, infos = env.step(actions)

        for agent in agents:
            ql_tables[agent].update(states[agent], observations[agent], actions[agent], rewards[agent], termination)
            record[i, env.agent_name_mapping[agent]] = actions[agent] if actions[agent] is not None else -1

        states = observations

    print(record)

#Function for the exploitation analysis. Gets called when a session is converged.
def explo_test(ql_tables, observations, states, actions, env, random_strat):

    record = np.zeros((4,1), dtype=np.int64)

    agents = env.possible_agents
    exploiter = random.randint(0, 1)

    if exploiter == 0:
        exploit_agent = agents[0]
        q_agent = agents[1]

    else:
        exploit_agent = agents[1]
        q_agent = agents[0]

    periods = 0
    end_count = 0
    end_crit = 1000
    end_threshold = 1
    if random_strat:
        end_threshold = 2

    actions = actions
    tot_rewards = {a: 0 for a in agents}


    for i in range(500000):
        actions[q_agent] = ql_tables[q_agent].get_action(observations[q_agent])
        ql_tables[q_agent].decay_epsilon()

        if random_strat:
            actions[exploit_agent] = random.randint(0, 2)
        else:
            actions[exploit_agent] = 0

        observations, rewards, termination, truncation, infos = env.step(actions)

        for a in agents:
            tot_rewards[a] += rewards[a]
        ql_tables[q_agent].update(states[q_agent], observations[q_agent], actions[q_agent], rewards[q_agent], termination)

        states = observations

        if actions[q_agent] <= end_threshold:
            end_count += 1
        else:
            end_count = 0

        if end_count >= end_crit:
            break

        periods += 1


    for i in range(1):
        record[i, :] = tot_rewards[agents[i]]
    record[2,:] = periods
    record[3,:] = exploiter
    print(record)
    print('exploiter:', exploit_agent, tot_rewards, periods)
