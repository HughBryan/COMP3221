import networkx as nx
import random
import matplotlib.pyplot as plt


def generate_random_topology(num_nodes,connections):
    G = nx.Graph()

    # Generate named nodes
    nodes = []
    for i in range(0,num_nodes+1):
        nodes.append(chr(ord('A')+i))

    G.add_nodes_from(nodes)

    connected_nodes = [nodes.pop(0)]


    # Recursisvely add nodes to the graph randomly.
    while (len(nodes)>0):
        node1 = random.choice(nodes)
        nodes.remove(node1)

        node2 = random.choice(connected_nodes)



        while (G.degree()[node2]>3):
            node2 = random.choice(connected_nodes)

        connected_nodes.append(node1)
        G.add_edge(node1,node2)

    # continously add links to other nodes.
    nodes = list(G.nodes)

    print(G.edges())    
    while (len(list(G.edges)) < connections):
        node1 = random.choice(nodes)
        while (G.degree()[node1] > 3):
            node1 = random.choice(nodes)
        node2 = random.choice(nodes)
        while (G.degree()[node2] > 3 or node1 == node2):
            node1 = random.choice(nodes)

        # Check if edge already exists:
        if (node1,node2) in list(G.edges()) or (node2,node1) in list(G.edges()):
            pass

        G.add_edge(node1,node2)

        # Get 2 nodes that have less than 1 degree each.

    return G

def assign_weights(G):
    weight = {}
    floor = 0.00
    top = 9.00



    for key in list(G.edges()):
        weight[key] = round(random.uniform(floor,top),1)


    nx.set_edge_attributes(G, values = weight, name = 'weight')



# Visual Display of Graph
def display_graph(G):
    plt.figure(figsize=(6, 4))
    pos = nx.spring_layout(G)  # positions for all nodes
    labels = nx.get_edge_attributes(G,'weight')
    nx.draw(G,pos,labels={node:node for node in G.nodes()},edge_color='blue',node_color='red')
    nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
    plt.show() 



graph = generate_random_topology(10,15)  
assign_weights(graph)
display_graph(graph)