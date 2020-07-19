from epanettools.epanettools import EPANetSimulation,Node,Link,Network,Nodes, Links,Patterns,Pattern,Controls,Control
from epanettools import epanet2 as et
import os


class Pump:

    def __init__(self, pump_id):
        self.id = pump_id
        self.status = [0]*25
        self.energy = [0]*25

    def set_status(self, hour, value):
        if value in [0,1]:
            self.status[hour] = value 
        else:
            raise Warning('pump status must be 0 or 1')
    def set_energy(self, hour, value):
        self.energy[hour] = value
    
    def get_status(self, hour):
        return self.status[hour]

    def get_results(self):
        return {"status":self.status, "energy":self.energy, "id":self.id}

class Tank:

    def __init__(self, tank_id):
        self.id = tank_id
        self.level = [0]*25

    def get_results(self):
        return {"level":self.level, "id":self.id}

    def set_level(self, hour, value):
        self.level[hour] = value

class Network:

    def __init__(self, inp_network_file, rpt_network_file):
        self.inp_file_path = os.path.abspath(inp_network_file)
        self.rpt_file_path = os.path.abspath(rpt_network_file)
        self.network_info = EPANetSimulation(self.inp_file_path)
        self._reset_nodes_links()

    def _reset_nodes_links(self):
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
        return self.pumps
    
    def set_pumps(self, pumps):
        for pump in pumps:
            if not isinstance(pump, Pump):
                raise Warning('must be pump object')
        self.pumps = pumps


    def get_tanks(self):
        return self.tanks

    def clean(self):
        self._reset_nodes_links()

    
    def simulate(self):
        ret=et.ENopen(self.inp_file_path, self.rpt_file_path, "")
        et.ENopenH()
        et.ENinitH(0)
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
                    pump.set_energy(inc, energy)

                for tank in self.tanks:
                    ret,tank_level=et.ENgetnodevalue(tank.id, et.EN_PRESSURE)
                    tank.set_level(inc, tank_level)
                
                ret,tstep=et.ENnextH()
                inc += 1
                if (tstep<=0):
                    break
        ret=et.ENcloseH()
    
    def get_results(self):
        results = {}
        results["pumps"] = [pump.get_results() for pump in self.pumps]
        results["tanks"] = [tank.get_results() for tank in self.tanks]
        return results

