import networkx as nx
import random
import matplotlib.pyplot as plt


def generate_random_topology(num_nodes,connections,max_connections = 3):
    G = nx.Graph()

    # Generate named nodes
    nodes = []
    for i in range(0,num_nodes+1):
        nodes.append(chr(ord('A')+i))
        G.add_node(nodes[i],port =6000+i)

    # Start with a single node that will be the basis for the connected graph.
    connected_nodes = [nodes.pop(0)]


    # Recursisvely add unnconnected nodes to the graph randomly.
    while (len(nodes)>0):
        node1 = random.choice(nodes)
        nodes.remove(node1)

        # From the connected nodes we select a a node that has <=3 connections. 
        node2 = random.choice(connected_nodes)
        while (G.degree()[node2]>max_connections):
            node2 = random.choice(connected_nodes)

        connected_nodes.append(node1)
        G.add_edge(node1,node2)


    # refresh node list so we can repeat process.
    nodes = list(G.nodes)

    # recurisevly add edges until we meet the edge requirement. Note that we have a maximum number of connections as denoted by the first variable in the funciton: max_connections.
    while (len(list(G.edges)) < connections):
        node1 = random.choice(nodes)
        while (G.degree()[node1] > max_connections):
            node1 = random.choice(nodes)
        node2 = random.choice(nodes)
        while (G.degree()[node2] > max_connections or node1 == node2):
            node2 = random.choice(nodes)


        # Check if edge already exists (if connection exists just reroll)
        if (node1,node2) in list(G.edges()) or (node2,node1) in list(G.edges()):
            pass

        G.add_edge(node1,node2)

    return G

# Add randomly assigned weights.
def assign_weights(G,floor = 0.00,ceiling = 9.00):
    weight = {}
    
    for key in list(G.edges()):
        weight[key] = round(random.uniform(floor,ceiling),1)

    nx.set_edge_attributes(G, values = weight, name = 'weight')
    G.edges(data=True)



# Visual Display of Graph
def display_graph(G):
    plt.figure(figsize=(6, 4))
    pos = nx.spring_layout(G)  # positions for all nodes
    labels = nx.get_edge_attributes(G,'weight')
    nx.draw(G,pos,labels={node:node for node in G.nodes()},edge_color='blue',node_color='red')
    nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
    plt.savefig('graph.png')
    plt.show() 
    

# Export graph
def export_graph(G):
    # dictionary containing nodes & weight to given neighbour. 
    node_neighbours = {}
    for edge in G.edges():
        # Do first node:
        if edge[0] not in node_neighbours:
            node_neighbours[edge[0]] = []
        if edge[1] not in node_neighbours:
            node_neighbours[edge[1]] = []
        weight = G.get_edge_data(edge[0],edge[1])['weight']
        node_neighbours[edge[0]].append((edge[1],weight))
        node_neighbours[edge[1]].append((edge[0],weight))

    for node in sorted(list(node_neighbours.keys())):
        with open("{}config.txt".format(node),"w") as file:
            file.write(str(len(node_neighbours[node]))+"\n")
            for neighbour_tuple in node_neighbours[node]:
                file.write("{} {} {}\n".format(neighbour_tuple[0],neighbour_tuple[1],G.nodes[neighbour_tuple[0]]['port']))



graph = generate_random_topology(10,15
                                 )  
assign_weights(graph)
export_graph(graph)

display_graph(graph)
