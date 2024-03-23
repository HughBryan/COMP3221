
import networkx as nx
import json

class NodeObj:

    def __init__(self,node,server_port, config):
        self.node = node
        self.host = "127.0.0.1"	
        self.server_port = server_port
        
        self.reroute_flag = True 
        self.node_online = True

        self.server_sockets = []
        self.client_sockets = []
        self.offline_client_sockets = []

        

        G = nx.Graph()
        G.add_node(node,port = server_port)
        try:
            with open(config,"r") as file:
                lines = int(file.readline())
                for i in range(0,lines):
                    line = file.readline().strip().split()
                    G.add_node(line[0],port = int(line[2]))
                    G.add_edge(node,line[0],weight =round(float(line[1]),1))

        except:
            raise Exception("Invalid config file")
        
        
        self.neighbour_ports = [int(G.nodes()[node]['port']) for node in G.neighbors(node)]

        self.G = G

        # List that will function as a queue of updated weights that will be sent via packets. 
        self.sending_queue = [[node,neighbour,G.get_edge_data(node,neighbour)['weight']] for neighbour in list(G.neighbors(node))]


    def encode_queue(self,queue) -> str:        

        if not queue:
            return str([]).encode("utf-8")
        return str(queue).encode("utf-8")



    def decode_topology(self,message) -> str:
        # Pass on the packets that we haven't seen yet. 
        message = message.decode("utf-8")        
        pass_on_packets = []

        try:
            message = message.replace("'",'"')
            packets_received = json.loads(message)
        except Exception as e:
            print(f"Error using json loading {message} {e}")
            return ""
        
        
        for edge in packets_received:


            # If we recieve a packet with only a single node, it means its marked for being down. 
            if len(edge) == 1:
                # If the graph has the node and is not the node marked for removal; remove it. 
                if self.G.has_node(edge[0]) and self.node != edge[0]:
                    self.G.remove_node(edge[0])
                    pass_on_packets.append(edge)
                    self.reroute_flag = True
                
            else:

                edge_weight  = round(float(edge[2]),1)
                if (edge[0],edge[1]) in self.G.edges() or (edge[0],edge[1]) in self.G.edges():
                    if self.G[edge[0]][edge[1]]["weight"] != edge_weight:
                        self.G[edge[0]][edge[1]]["weight"] = edge_weight
                        # Add flag for rerouting.
                        pass_on_packets.append(edge)
                        self.reroute_flag = True
                else:
        
                    self.G.add_edge(edge[0],edge[1])
                    self.G[edge[0]][edge[1]]["weight"] = edge_weight
                    # Add flag for rerouting.
                    self.reroute_flag = True
                    pass_on_packets.append(edge)

            self.sending_queue.extend(pass_on_packets)

        return packets_received


# NOT YET TESTED OR FULLY IMPLEMENTED.
    def disable_node(self):
        self.node_online = False
        self.reroute_flag = False
        
    def enable_node(self):
        self.node_online = True
        # Empty buffer to ensure that future messages are read in their entirety. 
        for sock in self.server_sockets:
            while sock.recv(3000):
                pass
    
    def remove_connection(self,socket):

        # Removes a connection on the graph found through the associated port.
        for node in list(self.G.neighbors(self.node) ):
            print(self.G.nodes()[node]['port'])

            if self.G.nodes()[node]['port'] == socket.getpeername()[1]:
                self.G.remove_node(node)
                print("Added elimination to queue")
                self.sending_queue.append([node])
        
        self.client_sockets.remove(socket)
        self.offline_client_sockets.append(socket)
        self.reroute_flag = True


    def add_connection(self,socket):
        try:
            self.client_sockets.append(socket)
            self.offline_client_sockets.remove(socket)
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
