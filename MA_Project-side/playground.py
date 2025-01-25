import itertools
NUM_AGENTS = 2
import numpy   as np

ETA = 0.1

print(range(1))
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
print(MOVESc)

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

##das gleiche für 2 und 3 wegen randomstrat:

demand2 = (np.e ** ((a1 - MOVESc[2]) / my)) / (
                np.e ** ((a1 - MOVESc[2]) / my) + np.e ** ((a1 - MOVESc[2]) / my) + 1)

demand3 = (np.e ** ((a1 - MOVESc[3]) / my)) / (
                np.e ** ((a1 - MOVESc[3]) / my) + np.e ** ((a1 - MOVESc[2]) / my) + 1)
print("2:", demand2 * (MOVESc[2] - Cost), "3:", demand3 * (MOVESc[3] - Cost))

##hier ist 2 besser! Müsste nochmal überlegen, was da genau der richtige Grenzwert sein sollte. Gibt ja schon eine optimal response
#zur randomchoice strategy

##mixed strategies:
def demand(pi, pj):
    demand = (np.e ** ((a1 - pi) / my)) / (
            np.e ** ((a1 - pi) / my) + np.e ** ((a1 - pj) / my) + 1)
    return demand

def profit_mix(price):
    profit = demand(price, MOVESc[0])*(price - Cost) + demand(price, MOVESc[1])*(price - Cost) + demand(price, MOVESc[2])*(price - Cost)
    print(profit)


for i in range(4):
    print(i)
    profit_mix(MOVESc[i])

##cool! Also genau genommen ist 1 die optimal response weiterhin! Könnte aber auch ein softeres Kriterium bezüglich Schadensbegrenzung bestimmen


#####__________________________________________


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

##protocol
###num_sessions fixed to 60
###Dann Liste mit unterschiedlichen tuples aus Funktionsinputs für main machen