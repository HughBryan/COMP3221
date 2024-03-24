
import networkx as nx
import json

class NodeObj:

    def __init__(self,node,server_port, config):
        self.config = config
        self.node = node
        self.host = "127.0.0.1"	
        self.server_port = server_port
        
        self.reroute_flag = True 
        self.node_online = True

        self.server_sockets = []
        self.client_sockets = []
        self.offline_client_sockets = []
        self.original_topology = [node]
        self.matching_ports = {}
        

        G = nx.Graph()
        G.add_node(node,port = server_port)
        try:
            with open(config,"r") as file:
                lines = int(file.readline())
                for i in range(0,lines):
                    line = file.readline().strip().split()
                    G.add_node(line[0],port = int(line[2]))
                    G.add_edge(node,line[0],weight =round(float(line[1]),1))
                    self.original_topology.append(line[0])

        except:
            raise Exception("Invalid config file")
        
        
        self.neighbour_ports = [int(G.nodes()[node]['port']) for node in G.neighbors(node)]

        self.G = G

        # List that will function as a queue of updated weights that will be sent via packets. 
        self.sending_queue = [[node,neighbour,G.get_edge_data(node,neighbour)['weight'],1] for neighbour in list(G.neighbors(node))]

    # Encode the code to send.
    def encode_queue(self,queue) -> str:        

        if not queue:
            return str([]).encode("utf-8")
        return str(queue).encode("utf-8")


    # Encoded topology will by default not propogate through the network.
    def send_topology_to_neighbours(self):
        topology = []
        for edge in self.G.edges():
            topology.append([edge[0],edge[1],self.G.get_edge_data(edge[0],edge[1])['weight'],0])
        return self.sending_queue.extend(topology)


    def decode_topology(self,message) -> str:
        # Pass on the packets that we haven't seen yet. 
        message = message.decode("utf-8")        
        pass_on_packets = []

        try:
            message = message.replace("'",'"')
            # Incase subsequent messages are sent.  
            message = message.replace("][",',')
            packets_received = json.loads(message)
        except Exception as e:
            print(f"Error using json loading {message} {e}")
            return ""
        
        
        for edge in packets_received:
            pass_on = False
            # If we recieve a packet with only a single node, it means its marked for being down. 
            if len(edge) == 2:
                # If the graph has the node and is not the node marked for removal; remove it. 
                if self.G.has_node(edge[0]) and self.node != edge[0]:
                    self.G.remove_node(edge[0])
                    self.reroute_flag = True

                    # if pass on packet is True
                    if bool(edge[1]) == True:
                        pass_on_packets.append(edge)

            else:
    
                print(edge)

                edge_weight  = round(float(edge[2]),1)
                # If the edge already exists and we need to update weight.
                if ((edge[0],edge[1]) in self.G.edges() or (edge[0],edge[1]) in self.G.edges()):
                    if self.G[edge[0]][edge[1]]["weight"] != edge_weight:
                        self.G[edge[0]][edge[1]]["weight"] = edge_weight
                        self.reroute_flag = True
                        
                        if bool(edge[3]) == True:
                            pass_on_packets.append(edge)     
                        
                # Edge doesn't exist and we need to add it. 
                else:
                    # readd connection if node becomes back online.
                    if edge[0] in self.original_topology and edge[1] in self.original_topology and not self.G.has_edge(edge[0],edge[1]):
                        for socket in self.offline_client_sockets:
                            if edge[0] in self.matching_ports and self.matching_ports[edge[0]] == socket:
                                self.add_connection(socket)
                            if edge[1] in self.matching_ports and self.matching_ports[edge[1]] == socket:
                                self.add_connection(socket)



                    self.G.add_edge(edge[0],edge[1])
                    self.G[edge[0]][edge[1]]["weight"] = edge_weight
                    self.reroute_flag = True
                    
                    if bool(edge[3]) == True:
                        pass_on_packets.append(edge)     

            

        self.sending_queue.extend(pass_on_packets)

        return packets_received


    def disable_node(self):
        self.node_online = False
        self.reroute_flag = False
        
    def enable_node(self):
        self.node_online = True
        
        # Add nodes ready for sending. 
        for neighbour in self.G.neighbors(self.node):
            self.sending_queue.append([self.node,neighbour,self.G.get_edge_data(neighbour,self.node)['weight'],1])
    
    def remove_connection(self,socket):
        print("Removed a connection!")
        # Removes a connection on the graph found through the associated port.
        for node in list(self.G.neighbors(self.node) ):
            initial_port = 6000
            inital_node = 'A'
            # Calculate what port the node is running on.
            if (ord(node)-ord(inital_node)+initial_port) == socket.getpeername()[1]:
                self.G.remove_node(node)
                print("Added elimination to queue")
                self.sending_queue.append([node,1])
        
        self.client_sockets.remove(socket)
        self.offline_client_sockets.append(socket)
        self.reroute_flag = True


    def add_connection(self,socket):
        try:
            self.client_sockets.append(socket)
            self.offline_client_sockets.remove(socket)
            self.send_topology_to_neighbours()
        except Exception as e:
            print(f"Error reconnecting with socket: {e}")
        
        # Send topology of 
    
    def update_connection(self,user_in):
        user_in = user_in.split(" ")
        if len(user_in) != 4:
            print("Invalid input. I.e., CHANGE A B 24")
            return
        node1 = user_in[1]
        node2 = user_in[2]
        weight = round(float(user_in[3]),1)

        if node1 not in self.G.nodes() or node2 not in self.G.nodes():
            print("One of the selected nodes doesn't exist.")
            return
        
        if ((node1,node2) in self.G.edges() or (node2,node1) in self.G.edges()):
            self.G[node1][node2]['weight'] = weight
        else:
            print(f"Connection does not exist to update: {node1} {node2}")


        self.sending_queue.append([node1,node2,weight])
