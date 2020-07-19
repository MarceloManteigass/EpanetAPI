from random import randint

from Network.network import Network


network = Network('./example_network.inp', './example_network.rpt')

#get pumps object
pumps = network.get_pumps()

#change this object according to your reinforcement learning agent
for pump in pumps:
    for hour in range(24):
        value = randint(0, 1)
        pump.set_status(hour, value)

network.set_pumps(pumps)
network.simulate()
results = network.get_results()
print(results)



