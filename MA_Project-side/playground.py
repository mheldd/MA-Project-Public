import itertools
NUM_AGENTS = 2
import numpy   as np

lbound = 1.5
hbound = 2
NUM_PRICES = 15
MOVES = list(range(NUM_PRICES))
OBSERVATIONS = list(itertools.product(MOVES, repeat=NUM_AGENTS))
print(len(OBSERVATIONS))
a1 = 2
my = 1/4
Cost = 1
delta = 0.95
MOVESc = np.linspace(lbound, hbound, NUM_PRICES)

list = []

for a in MOVESc:
    rewards = 0
    for b in MOVESc:
        demand = (np.e ** ((a1 - a) / my)) / (
                np.e ** ((a1 - a) / my) + np.e ** ((a1 - b) / my) + 1)
        rewards += demand * (a - Cost)
    list.append((rewards/((1-delta)*NUM_PRICES)))

print(sum(list)/len(list))
#print(list)

init = np.zeros((NUM_PRICES**2, NUM_PRICES))

for i in range(NUM_PRICES):
    init[:, i] = list[i]

print(init)


demand = (np.e ** ((a1 - MOVESc[0]) / my)) / (
                np.e ** ((a1 - MOVESc[0]) / my) + np.e ** ((a1 - MOVESc[0]) / my) + 1)
rewards = demand * (MOVESc[0] - Cost)
print(rewards/((1-delta)))

#print(np.e**(-((10**(-4))*10000)))

#Do it like Schmalvano
import random
for i in range(1000):
    print(random.randint(0, 4))