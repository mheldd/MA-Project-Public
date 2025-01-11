import itertools
NUM_AGENTS = 2
import numpy   as np

ETA = 0.1

PNASH = 1.47293
PMONOP = 1.92498

LBOUND = PNASH - ETA*(PMONOP - PNASH)
#LBOUND = 1
HBOUND = PMONOP + ETA*(PMONOP - PNASH)
NUM_PRICES = 15
MOVES = list(range(NUM_PRICES))
OBSERVATIONS = list(itertools.product(MOVES, repeat=NUM_AGENTS))
print(len(OBSERVATIONS))
a1 = 2
my = 1/4
Cost = 1
delta = 0.95
MOVESc = np.linspace(LBOUND, HBOUND, NUM_PRICES)

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

demand0 = (np.e ** ((a1 - MOVESc[0]) / my)) / (
                np.e ** ((a1 - MOVESc[0]) / my) + np.e ** ((a1 - MOVESc[0]) / my) + 1)

demand1 = (np.e ** ((a1 - MOVESc[1]) / my)) / (
                np.e ** ((a1 - MOVESc[1]) / my) + np.e ** ((a1 - MOVESc[0]) / my) + 1)
print("1:", demand1 * (MOVESc[1] - Cost), "0:", demand0 * (MOVESc[0] - Cost))

##1 ist besser!

init = np.zeros((NUM_PRICES**2, NUM_PRICES))

for i in range(NUM_PRICES):
    init[:, i] = list[i]

print(init)


demand = (np.e ** ((a1 - MOVESc[0]) / my)) / (
                np.e ** ((a1 - MOVESc[0]) / my) + np.e ** ((a1 - MOVESc[0]) / my) + 1)
rewards = demand * (MOVESc[0] - Cost)
print(rewards/((1-delta)))

#print(np.e**(-((10**(-4))*10000)))


print(range(NUM_PRICES))

print(np.linspace(2*10**(-5), 0, 100))

#möglicher grid: 1.5*10**(-5), 10**(-5), 5.25*10**(-6)
#oder minimum 2*10**-5 als Ausgnagspunkt nehmen und dann bisschen erhöhen