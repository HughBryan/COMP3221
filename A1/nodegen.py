import networkx as nx
import random
import matplotlib.pyplot as plt
import heapq

def generate_random_topology(num_nodes,connections,max_connections = 3):
    G = nx.Graph()

    # Generate named nodes
    nodes = []
    for i in range(0,num_nodes):
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
    nodes = list(G.nodes())

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
def assign_weights(G,floor = 0.1,ceiling = 9.00):
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
    nx.draw(G,pos, labels={node:node for node in G.nodes()},edge_color='blue',node_color='red')
    nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
    plt.show() 
    



# Visual Display of Graph
def save_graph_png(G,name = "graph.png"):
    plt.figure(figsize=(6, 4))
    pos = nx.spring_layout(G)  # positions for all nodes
    labels = nx.get_edge_attributes(G,'weight')
    nx.draw(G,pos, labels={node:node for node in G.nodes()},edge_color='blue',node_color='red')
    nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
    plt.savefig(name)



# Export graph into config files.
def export_graph_as_config(G):
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



# Function that takes in a graph and a starting node and outputs shortest path to all other nodes.
def routing_table(G,starting_node):
    
    # A node dictionary that has shortest current distance to each node (with path)
    shortest_path = {starting_node:(0,starting_node)}
    dist_index = 0
    predecessor_index = 1

    # Heap queue.
    queue = []
    unvisted_nodes = list(G.nodes())
    curr_node = starting_node

    # Get shortest paths
    while (unvisted_nodes):
        for neighbor in G.neighbors(curr_node):
            # add all neighbors to priority queue based on total distance. Edge weight + previous total distance. 
            node_dist = (G.get_edge_data(curr_node,neighbor)['weight'])+shortest_path[curr_node][dist_index]
            predecessor = shortest_path[curr_node][predecessor_index]
            
            # if the neighbor has not yet been encountered we add it to the queue.
            if neighbor not in shortest_path:
                heapq.heappush(queue,(node_dist,neighbor))

            # if the neighbor is in the known distance dict, we check whether it is a better path. If it is, we replace it. 
            if neighbor in shortest_path:
                if shortest_path[neighbor][dist_index] > node_dist:
                    shortest_path[neighbor] = (node_dist,predecessor+neighbor)

            # If the node is not the known distance dict, we simply add it. 
            else:
                shortest_path[neighbor] = (node_dist,predecessor+neighbor)


        unvisted_nodes.remove(curr_node)

        # If queue is not empty we get next item.     
        if queue:
            curr_node = heapq.heappop(queue)[1]



    # Remove inital starting point for ease of printing (i.e., remove path A to A as its redundant)
    del shortest_path[starting_node]


    # Format routing table. 
    print(f"I am node {starting_node}")
    for node in sorted(list(shortest_path.keys())):
        print(f"Least cost path from {starting_node} to {node}: {shortest_path[node][predecessor_index]}, link cost: {round(float(shortest_path[node][dist_index]),1)}")







if __name__ == "__main__":  
    graph = generate_random_topology(3,2)  
    assign_weights(graph)
    export_graph_as_config(graph)


    
    
    display_graph(graph)    
    save_graph_png(graph)
    #routing_table(graph,'A')

