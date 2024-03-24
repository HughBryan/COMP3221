
import sys
import networkx as nx
import nodegen
import threading
import socket
import select
import time
from NodeObj import NodeObj


# Function to accept commands.
def command_line_interface(node_obj):
    while True:
        try:
            user_in = input("Enter Command: ")
            if user_in.upper() == "DOWN" and node_obj.node_online:
                node_obj.disable_node()


            elif user_in.upper() == "UP" and node_obj.node_online:
                    node_obj.enable_node()

            elif user_in.upper().startswith("CHANGE"):
                try:
                    node_obj.update_connection(user_in)
                except: print("Invalid input. I.e., CHANGE A B 24")
            
            else:
                print("Invalid command.")

        except KeyboardInterrupt:
            print("Interrupted by user. Shuttdowning down sockets.")

            for socket in node_obj.server_sockets:
                socket.close()
            for socket in node_obj.client_sockets:
                socket.close()


# Rerouter. 
def rerouter(node_obj):
    inital_sleep = 0
    time.sleep(inital_sleep)
    default_timeout = 10
    while True:
        if (node_obj.reroute_flag and node_obj.node_online):
            node_obj.reroute_flag = False
            nodegen.routing_table(node_obj.G,node_obj.node)
            time.sleep(default_timeout)



# Create a server and listen for incoming connections from neighbouring ports.
def create_server_and_listen(node_obj):
    buffer = 4096

    host_port = node_obj.server_port
    host = node_obj.host
    expected_connections = len(node_obj.neighbour_ports)

    # Create socket object to act as server. 
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # solution for "[Error 89] Address already in use". Use before bind()
    s.bind((host, host_port))
    s.listen(expected_connections) # Number of connections is the number of neighbours in the graph.

    sockets = node_obj.server_sockets


    # Connect to all clients that are trying to connect. Number of connections expected is the number of neighbours.
    try:
        while len(sockets) != expected_connections:
            conn, addr = s.accept()
            sockets.append(conn)

    except KeyboardInterrupt:
        print("Stopped by Ctrl+C")
    
    # We are now ready to send data packets. 
    node_obj.ready_to_send = True
    # Listen to messages forever. 
    while True:
        # Select returns ready sockets that have information in them.
        if node_obj.server_sockets and node_obj.node_online:
            ready_socks,_,_ = select.select(node_obj.server_sockets, [], []) 


            for sock in ready_socks:
                    # check if it is an offline node. If it is, we turn it online. 
                    data = sock.recv(buffer) 
                    if not data:
                        sock.close()
                        sockets.remove(sock)

                    # Decode messages recieved.
                    else: 
                        message = node_obj.decode_topology(data)
                        sock.send(b"Recieved")
            




# Establish connections with neighbours. 
def establish_connections(node_obj):
    default_timeout = 60
    inital_port = 6000
    buffer = 4096
    host = node_obj.host

    for port in node_obj.neighbour_ports:

        connected = False
        while not connected:    
            try:
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM,)
                s.connect((host,port))
                node_obj.client_sockets.append(s)
                # The target port will correspond with the socket that attaches to it. 
                node_obj.matching_ports[chr(port-inital_port+ord('A'))] = s
                connected = True

            except Exception as e:
                print(f"Failed connecting to {port}")
                time.sleep(5)

    while node_obj.ready_to_send:
        # Get all new links. Designed in a way such that we never miss information.
        if node_obj.node_online:
            queue = node_obj.sending_queue
            node_obj.sending_queue = []
            
            for sock in node_obj.client_sockets:
                try:
                    # send topology
                    sock.send(node_obj.encode_queue(queue))


                    # Wait 2 seconds for return. If it does not return, we can assume that node is down. 
                    timeout = 2
                    ready_sock,_,_ = select.select([sock], [], [],timeout) 
                    
                    # If we didn't receieve a response, we can only assume that the node is offline. 
                    if not ready_sock:
                        node_obj.remove_connection(sock)
                    else:
                        message = sock.recv(buffer).decode("utf8")

                except ConnectionResetError:
                    pass
            
            
            time.sleep(default_timeout)






#python COMP3221_A1_Routing.py F 6005 Fconfig.txt

if __name__ == "__main__":
    print("Welcome. Commannds are 'DOWN', 'UP', 'CHANGE *NODE1 *NODE2 *WEIGHT'")
    print("Changes to weights must be done for existing connections of this given node.")
    # Startup. Get commandline arguments etc.

    if (len(sys.argv) < 4):
        raise Exception("Insufficient Command-Line Arguments")

    node = sys.argv[1]
    port_number = int(sys.argv[2])
    config = sys.argv[3]

    node_obj = NodeObj(node,port_number,config)


    # Listening Thread / Server thread
    listen_thread = threading.Thread(target=create_server_and_listen,args=(node_obj,))
    listen_thread.start()

    # Sending thread
    sending_thread = threading.Thread(target = establish_connections,args = (node_obj,))
    sending_thread.start()

    # Routing Calculation thread
    route_thread = threading.Thread(target = rerouter,args = (node_obj,))
    route_thread.start()

    command_line_interface(node_obj)