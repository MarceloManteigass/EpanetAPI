from epanettools.epanettools import EPANetSimulation ,Node, Link, Network, Nodes, Links, Patterns ,Pattern, Controls, Control
from epanettools import epanet2 as et
import os

import matplotlib.pyplot as plt


class Pump:
    """
    This class describes a general pump from the network. For a certain pump the its status
    (open or close) can be set before the simulation, and the energy spent pumping can be 
    retrieve after the simulation. The increments are set by default in hourly basis

    Parameter
    ---------
    pump_id : string
        unique identifier that distinguishes a single pump in the network
    """

    def __init__(self, pump_id):
        self.id = pump_id
        """initialize with zeros the pump X status and the energy"""
        self.status = [0]*25 #status of the pump - 0 for off, 1 for on
        self.energy = [0]*25 #energy value of the pump in Kwh

    def set_status(self, hour, value):
        """
        set the status of pump X, in increment y the value(0 or 1) z
        """
        if value in [0,1]:
            self.status[hour] = value 
        else:
            raise Warning('pump status must be 0 or 1')
    
    def get_status(self, hour):
        """
        get the status of pump X, in increment y the value(0 or 1) z
        """
        return self.status[hour]

    def set_energy(self, hour, value):
        """
        set the energy of pump X, in increment y the value z(Kwh)
        """
        self.energy[hour] = value
    
    def get_inc(self):
        """
        return the number o increments used in a simulation. 24 increments representing 24 hours
        """
        return len(self.status)

    def get_results(self):
        """
        returns the results of energy and status for a pump during the 24 increments (1 day long)
        after the simulation has been done
        """
        return {"status":self.status, "energy":self.energy, "id":self.id}

class Tank:
    """
    This class describes a general tank from the network. For a given tank, the water level 
    is measured in meters for the default 24 hours increments.

    Parameter
    ---------
    tank_id : string
        unique identifier that distinguishes a single tank in the network
    """

    def __init__(self, tank_id):
        self.id = tank_id
        """initialize with zeros the tank X water level"""
        self.level = [0]*25 #this value is set during the simulation

    def set_level(self, hour, value):
        """
        set the water level of tank X, in increment y the value z(Kwh)
        """
        self.level[hour] = value

    def get_results(self):
        """
        returns the results of water level for a tank during the 24 increments (1 day long)
        after the simulation has been done
        """
        return {"level":self.level, "id":self.id}

class Network:
    """
    This class represents the network as described in the inp and rpt files

    Parameter
    ---------
    inp_network_file : path to inp network file
    inp_network_file : path to rpt file
        these files are created through the epanet software. Once the newtowrk is completly modeled
        you can export these files.
    """

    def __init__(self, inp_network_file, rpt_network_file):
        self.inp_file_path = os.path.abspath(inp_network_file)
        self.rpt_file_path = os.path.abspath(rpt_network_file)
        self.network_info = EPANetSimulation(self.inp_file_path)
        self._reset_nodes_links()

    def _reset_nodes_links(self):
        """
        Creates a pump instance and a tank instance to work with in the simulation for each one 
        in the network, and sets their values to zero
        """
        node_types = {v: k for k, v in Node.node_types.items()}
        link_types = {v: k for k, v in Link.link_types.items()}
        self.pumps = []
        self.tanks = []

        for node in self.network_info.network.nodes:
            if node_types[self.network_info.network.nodes[node].node_type] == "TANK":
                self.tanks.append(Tank(node))

        for link in self.network_info.network.links:
            if link_types[self.network_info.network.links[link].link_type] == "PUMP":
                self.pumps.append(Pump(link))

    def get_pumps(self):
        """
        return the pumps of the network to change before the simulation
        """
        return self.pumps
    
    def set_pumps(self, pumps):
        """
        sets the pumps after being changed
        """
        for pump in pumps:
            if not isinstance(pump, Pump):
                raise Warning('must be pump object')
        self.pumps = pumps


    def get_tanks(self):
        """
        returns tanks from the network
        """
        return self.tanks

    def clean(self):
        """
        cleans the tanks and pump values in case of recurring simulations
        """
        self._reset_nodes_links()

    
    def simulate(self):
        """
        simulates the network using the pump status established before running the simulation.
        in the simulation it's considered an hourly increment, therefore, at every hour it's set the
        pump status and it's read the tank water level value
        """
        ret=et.ENopen(self.inp_file_path, self.rpt_file_path, "")
        et.ENopenH()
        et.ENinitH(1)
        inc = 0
        while True:
            ret,t=et.ENrunH()
            if t%3600!=0:
                ret,tstep=et.ENnextH()
                if (tstep<=0):
                    break
            else:   
                for pump in self.pumps:
                    ret=et.ENsetlinkvalue(pump.id,et.EN_STATUS,pump.get_status(inc))
                    ret,energy=et.ENgetlinkvalue(pump.id,et.EN_ENERGY)
                    ret,status=et.ENgetlinkvalue(pump.id,et.EN_STATUS)
                    pump.set_energy(inc, energy)
                    pump.set_status(inc, status)

                for tank in self.tanks:
                    ret,tank_level=et.ENgetnodevalue(tank.id, et.EN_PRESSURE)
                    tank.set_level(inc, tank_level)
                
                ret,tstep=et.ENnextH()
                inc += 1
                if (tstep<=0):
                    break
        ret=et.ENcloseH()
        et.ENsavehydfile("./simulation_result.bin")
        et.ENclose()
    
    def get_results(self, visualize_results = False):
        """
        returns the values of the pumps and tanks after simulation is finished
        """
        results = {}
        results["pumps"] = [pump.get_results() for pump in self.pumps]
        results["tanks"] = [tank.get_results() for tank in self.tanks]
        if visualize_results:
            self._visualize_results()
        return results
    
    def _visualize_results(self):
        """
        creates a plot to visualize the results
        """
        n_plots = max([len(self.pumps), len(self.tanks)])
        fig, axs = plt.subplots(3, n_plots)
        fig.suptitle('Simulation Results')
        for i, pump in enumerate(self.pumps):
            pump_results = pump.get_results()
            axs[0, i].plot(range(0,25), pump_results["status"])
            axs[0, i].set_title("pump-{}-status(on/off)".format(pump_results["id"]))
            axs[1, i].plot(range(0,25), pump_results["energy"])
            axs[1, i].set_title("pump-{}-energy(kwh/hour)".format(pump_results["id"]))
        for j, tank in enumerate(self.tanks):
            tank_results = tank.get_results()
            axs[2, j].plot(range(0,25), tank_results["level"])
            axs[2, j].set_title("tank-{}-water-level(m/hour)".format(tank_results["id"]))
        plt.show()
