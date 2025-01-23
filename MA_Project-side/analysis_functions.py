import numpy as np
import random


def conv_logging(ql_tables, observations, states, actions, env):
    check_duration = 15
    agents = env.possible_agents
    actions = actions

    record = np.zeros((check_duration, 2), dtype=np.float32)


    for i in range(0, check_duration):
        for agent in agents:
            actions[agent] = ql_tables[agent].get_action(observations[agent])
            ql_tables[agent].decay_epsilon()

        observations, rewards, termination, truncation, infos = env.step(actions)

        #save actions of agents to column 0 and 1
        for agent in agents:
            record[i, env.agent_name_mapping[agent]] = actions[agent] if actions[agent] is not None else -1
            ql_tables[agent].update(states[agent], observations[agent], actions[agent], rewards[agent], termination)

        states = observations

    return record




##Function for the impulse response analysis. Gets called when a session is converged.
def impulse_response(ql_tables, observations, states, actions, env, dev_action, dev_duration):

    agents = env.possible_agents
    actions = actions
    deviator = agents[0]
    q_player = agents[1]

    conv_check_duration = 15
    response_check_duration = 150
    total_duration = conv_check_duration+response_check_duration
    record = np.zeros((total_duration, 2), dtype=np.int64)

    for i in range(0, total_duration):
        if conv_check_duration < i <= conv_check_duration+dev_duration:
            actions[deviator] = dev_action
            actions[q_player] = ql_tables[q_player].get_action(
                observations[q_player])
        else:
            for agent in agents:
                actions[agent] = ql_tables[agent].get_action(observations[agent])

        observations, rewards, termination, truncation, infos = env.step(actions)

        for agent in agents:
            ql_tables[agent].update(states[agent], observations[agent], actions[agent], rewards[agent], termination)
            record[i, env.agent_name_mapping[agent]] = actions[agent] if actions[agent] is not None else -1

        states = observations

    return record

#Function for the exploitation analysis. Gets called when a session is converged.
def explo_test(ql_tables, observations, states, actions, env, dev_action, random_strat):
    conv_check_duration = 15
    response_check_duration = 150
    total_check_duration = conv_check_duration + response_check_duration
    record = np.zeros((total_check_duration+2, 2), dtype=np.int64)

    agents = env.possible_agents

    exploit_agent = agents[0]
    q_agent = agents[1]

    periods = 0
    end_count = 0
    end_crit = 1000
    end_threshold = 1
    if random_strat:
        end_threshold = 2

    tot_rewards = {a: 0 for a in agents}


    for i in range(500000):
        if i < conv_check_duration:
            for a in agents:
                actions[a] = ql_tables[a].get_action(observations[a])
                ql_tables[a].decay_epsilon()
        else:
            actions[q_agent] = ql_tables[q_agent].get_action(observations[q_agent])
            ql_tables[q_agent].decay_epsilon()
            if random_strat:
                actions[exploit_agent] = random.randint(0, 2)
            else:
                actions[exploit_agent] = dev_action

        observations, rewards, termination, truncation, infos = env.step(actions)

        for a in agents:
            #store sum of rewards after the deviation
            if i >= conv_check_duration:
                tot_rewards[a] += rewards[a]
            #store the first 150 actions after the deviation
            if periods <= total_check_duration:
                record[i, env.agent_name_mapping[a]] = actions[a] if actions[a] is not None else -1

        ql_tables[q_agent].update(states[q_agent], observations[q_agent], actions[q_agent], rewards[q_agent], termination)

        states = observations

        if actions[q_agent] <= end_threshold:
            end_count += 1
        else:
            end_count = 0

        if end_count >= end_crit:
            break

        periods += 1

    record[total_check_duration, :] = periods - conv_check_duration - end_crit
    record[total_check_duration+1, 0] = tot_rewards[agents[0]]
    record[total_check_duration+1, 1] = tot_rewards[agents[1]]


    return record
