
import sys
import networkx as nx
import nodegen
import threading
import socket
import select
import time
from NodeObj import NodeObj

# Function to accept commands.
def command_line_interface(node_obj,t1,t2,t3):
    while True:
        try:
            user_in = input("Enter Command: ")
            if user_in.upper() == "DOWN":
                # node offonline  
                node_obj.disable_node()


            if user_in.upper() == "UP":
                node_obj.enable_node()

            if user_in.upper().startswith("CHANGE"):
                try:
                    node_obj.update_connection(user_in)
                except: print("Invalid input. I.e., CHANGE A B 24")

        except KeyboardInterrupt:
            print("Interrupted by user. Shuttdowning down threads.")
            t1.set()
            t2.set()
            t3.set()
            for socket in node_obj.server_sockets:
                socket.close()
            for socket in node_obj.client_sockets:
                socket.close()


# Rerouter. 
def rerouter(node_obj):
    while True:
        if (node_obj.reroute_flag and node_obj.node_online):
            node_obj.reroute_flag = False
            nodegen.routing_table(node_obj.G,node_obj.node)
            time.sleep(10)



# Create a server and listen for incoming connections from neighbouring ports.
def create_server_and_listen(node_obj):

    host_port = node_obj.server_port
    host = node_obj.host
    expected_connections = len(node_obj.neighbour_ports)

    # Create socket object to act as server. 
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # solution for "[Error 89] Address already in use". Use before bind()
    s.bind((host, host_port))
    s.listen(expected_connections) # Number of connections is the number of neighbours in the graph.

    sockets = node_obj.server_sockets

    print("Server hosted on port {}".format(host_port))

    # Connect to all clients that are trying to connect. Number of connections expected is the number of neighbours.
    try:
        while len(sockets) != expected_connections:
            print("Waiting for client")
            conn, addr = s.accept()
            sockets.append(conn)
            print(f"Server connected to: {s.getsockname()[1]}",)

    except KeyboardInterrupt:
        print("Stopped by Ctrl+C")
    
    # Listen to messages forever. 
    while True:
        # Select returns ready sockets that have informaiton in them.
        if node_obj.server_sockets and node_obj.node_online:
            ready_socks,_,_ = select.select(node_obj.server_sockets, [], []) 
        
            for sock in ready_socks:
                    if sock in node_obj.offline_client_sockets:
                        node_obj.add_connection(sock)

                    data = sock.recv(4096) 
                    if not data:
                        sock.close()
                        sockets.remove(sock)

                    # Decode messages recieved.
                    else: 
                        message = node_obj.decode_topology(data)
                        print(f"Received message:",message)
                        sock.send(b"Recieved")
            




# Establish connections with neighbours. 
def establish_connections(node_obj):

    host = node_obj.host

    for port in node_obj.neighbour_ports:

        connected = False
        while not connected:    
            try:
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM,)
                s.connect((host,port))
                node_obj.client_sockets.append(s)
                connected = True
                print(f"Client connected to {port}")

            except Exception as e:
                print(f"Failed connecting to {port}: {e}")
                time.sleep(5)

    while True:
        # Get all new links. Designed in a way such that we never miss information.
        if node_obj.node_online:
            queue = node_obj.sending_queue
            node_obj.sending_queue = []
            
            for sock in node_obj.client_sockets:
                try:
                    # send topology
                    sock.send(node_obj.encode_queue(queue))


                    # Wait 3 seconds for return. If it does not return, we can assume that node is down. 
                    timeout = 3
                    ready_sock,_,_ = select.select([sock], [], [],timeout) 
                    if not ready_sock:
                        node_obj.remove_connection(sock)
                    else:
                        message = sock.recv(4096).decode("utf8")
                        if message == "Recieved":
                            print(f"Socket recieved")
                        else:
                            print(f"Unknown message recieved: {message}")
                except ConnectionResetError:
                    pass
            time.sleep(10)






#python COMP3221_A1_Routing.py F 6005 Fconfig.txt

if __name__ == "__main__":
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

    command_line_interface(node_obj,listen_thread,sending_thread,route_thread)