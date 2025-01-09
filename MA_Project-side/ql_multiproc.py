import ql_agent

import env_aec_disc_15
import env_pl_disc
import multiprocessing


q_result = []

def run_session(session_id, env):
    observations, infos = env.reset()
    agents = env.possible_agents

    ql_tables = {agent: ql_agent.QLAgent(env) for agent in agents}



    actions = {agent: 99 for agent in agents}
    states = {agent: 999 for agent in agents}

    last_ten = []

    while env.agents:
        for agent in agents:
            actions[agent] = ql_tables[agent].get_action(observations[agent])
            ql_tables[agent].decay_epsilon()

        if ql_tables[agents[0]].num_moves > 999990:
            last_ten.append(actions)


        observations, rewards, termination, truncation, infos = env.step(actions)

        for agent in agents:
            if ql_tables[agent].num_moves > 1:
                ql_tables[agent].update(states[agent], observations[agent], actions[agent], rewards[agent], termination)

        states = observations



    env.close()


    return f"Session {session_id} complete", last_ten

def main():
    num_sessions = multiprocessing.cpu_count()
    #env = env_aec_disc_15.env(render_mode=None)
    env = env_pl_disc.parallel_env(render_mode=None)

    with multiprocessing.Pool(processes=num_sessions) as pool:
        results = pool.starmap(
            run_session,
            [(i, env) for i in range(num_sessions)],
        )
        print(results)



if __name__ == "__main__":
    main()



