
import networkx as nx
import json

class NodeObj:

    def __init__(self,node,server_port, config):
        self.node = node
        self.host = "127.0.0.1"	
        self.server_port = server_port
        self.nodeonline = True
        self.server_sockets = []
        self.client_sockets = []
        self.reroute_flag = False

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
        self.sending_queue = [(node,neighbour,G.get_edge_data(node,neighbour)['weight']) for neighbour in list(G.neighbors(node))]

        
    def encode_topology(self):
        G = self.G
        message = []
        for edge in G.edges():
            edge_str = list(edge)
            edge_str.append(G.get_edge_data(edge[0],edge[1])['weight'])
            message.append(str(edge_str))
        
        message =str(":".join(message)).encode("utf-8")
        return message

    def decode_topology(self,message):
        message = message.decode("utf8")
        message = message.replace("'",'"').split(":")
        for edge in message:

            edge = json.loads(edge)
            edge_weight  = round(float(edge[2]),1)
            if (edge[0],edge[1]) in self.G.edges() or (edge[0],edge[1]) in self.G.edges():
                if self.G[edge[0]][edge[1]]["weight"] != edge_weight:
                    self.G[edge[0]][edge[1]]["weight"] = edge_weight
                    # Add flag for rerouting.
                    self.reroute_flag = True
            else:
     
                self.G.add_edge(edge[0],edge[1])
                self.G[edge[0]][edge[1]]["weight"] = edge_weight
                # Add flag for rerouting.
                self.reroute_flag = True

        return message
