# HOW TO USE:

- Each node must be launched in its own terminal. I.e., COMP3221_A1_ROUTING.py A 6000 Aconfig.txt. Once all nodes are connected the user can watch information propogate the network accordingly. 
TO USE CLI PROPERLY: WAIT FOR INFORMATION TO FULLY PROPOGATE NETWORK BEFORE ENTERING CONFLICTING INFORMATION (I.E., UP AND DOWN QUICKLY WILL RESULT WITH A LOOP WITHIN TOPOLOGY)
USER OPTIONS TO TYPE INTO CLI:
- 'DOWN': marks the node as down and information will propogate through network.
- 'UP': marks the node as up and information will propogate throughj network.
- 'CHANGE node1 node2 weight'. Changes a weight for a local weight to that node. The connection must already exist. I.e., 'Change A B 12'. 

To close the program, the terminal must be fully closed. This will result with failure of other nodes that will have to be subsequentially be closed. 

# Nodegen.py

## Dependencies:

- Networkx. Simple networking package as outlined in the tutorials. Only used to give help give visual aid and to be used as a graph data structure.
- random. Random is a package that is only used to select random nodes for connection and to assign random weights.
- matplotlib.pyplot. Matplotlib is only used for displaying the graph.
- heapq. Heapq package that is used to implement a priority queue in the routing algorithm.

## Functions:

- generate_random_topology: Function that outputs a random fully connected graph based on a given number of nodes and connections.
- assign_weights: Assigns random weights to each edge in the graph that is parsed to it. By default, it is between 0.1 and 9.
- display_graph: Displays a given graph.
- save_graph_png: Saves a graph as a png. Used for debugging and giving visual aid.
- export_graph_as_config: Exports the graph as a given number of config files in the format outlined in the spec.
- routing_table: Given a graph and a starting node, outputs the entire routing table for that node and the table.

# NodeObj.py

## Functionality:

This file is home to a single class (node_obj), that houses all the functionality required with a specific node. A single node has a lot of information associated with it; the config, node name, host, port, sockets etc.

## Functions:

- **init**: The initial call to create an object of this class will create a new node object from a given node name, server_port and config file. There is no error checking that the correct port and config file have been given. Will begin by adding to its send queue all the information about its neighbours. Additionally begins by constructing the initial graph that will graph as the graph propagates.
- encode_queue: returns an encoded string version of the sending queue.
- send_topology_to_neighbours: sends the nodes local topology to neighbours. This information will not be propogated through the network and is only used when a node requests information on being re-booted.
- decode_topology: A substantial function that is responsible for reading the encoded packets that are sent. These packets are decoded and added to the topology (where necessary).
- disable_node: disables a node (stop receiving packets)
- enable_node: enables a node and sends a packet to its neighbours of its edge data.
- remove_connection: remove a socket connection as a node has been detected down.
- add_connection: re-adds the socket connection to the given nodes topology.
- update_connection: updates a given as outlined by command-line interface (and sends the updated packet)

# COMP3221_A1_Routing.py

## Functionality:

The program launches 3 seperate threads: listening thread (create_sever_and_listen), sending_thread (establish_connections) and rerouting thread (rerouter). These three threads access the same node obj but run simultaneously.

## Functions:

- command_line-interface: Simulates the command line interface for the 3 given functionalities.
- create_server_and_listen: Creates a server for a node object. Listens on that port for given connections and interprets packets.
- establish_clients: establishes client sockets for each of its neighbours. Is responsible for sending through packets and detecting when nodes becomes disabled.
- Rerouter: If a change occurs we print out the routing table. Happens every 10 seconds.
