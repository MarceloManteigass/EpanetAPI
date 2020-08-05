from random import randint
from tqdm import tqdm


class NetworkManagement:
    """
    This class uses the results of various simulations to train a control model
    used to optimally control the network
    """
    def __init__(self, network):
        self.network = network

    def train(self):
        """
        I'm using a random function, but here should be where you use
        your reinforcement learning agent, to run many diferent simulations
        interpret the results and learn an optimized control model
        """
        self.loss = 1000000
        for iter in tqdm(range(1000)):
            self.network.clean()
            self.pumps = self.network.get_pumps()
            for pump in self.pumps:
                for inc in range(pump.get_inc()):
                    value = randint(0, 1)
                    pump.set_status(inc, value)
            self.network.set_pumps(self.pumps)
            self.network.simulate()
            results = self.network.get_results(visualize_results=False)
            energy_spent = sum([sum(pump["energy"]) for pump in results["pumps"]]) #get total energy spent
            total_water_level = sum([tank["level"][-1] for tank in results["tanks"]]) + 1 #get total water level in the end of simulation
            #dummy loss function to find best pump status, maximize water in the tank and minimize energy spent
            if energy_spent*(1/total_water_level) < self.loss:
                self.loss = energy_spent*(1/total_water_level)
                self.best_pumps = self.pumps

    def control(self):
        """
        return the best pump status combination to control the network
        """
        print(self.best_pumps)
        return self.best_pumps
