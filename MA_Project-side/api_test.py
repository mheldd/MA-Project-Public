from pettingzoo.test import parallel_api_test, api_test

import env_aec_disc_15



parallel_api_test(env_aec_disc_15.env(), num_cycles=1000)

