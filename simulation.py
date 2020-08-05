from Network.network import Network
from Model.network_management_model import NetworkManagement

#Create the network simulation object
network = Network('./example_network.inp', './example_network.rpt')

#Create the network management object
control_model = NetworkManagement(network)
#train the object by defining a learning model
control_model.train()
#after training get the best pump status to control your network acording to your model
pumps = control_model.control()
#set those pump values in the network object
network.set_pumps(pumps)
#simulate the network with the best pump status your model found
network.simulate()
#get results in dictionary structure and visualize the results
results = network.get_results(visualize_results=True)
print(results)



