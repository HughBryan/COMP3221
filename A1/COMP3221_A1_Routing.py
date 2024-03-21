
import sys
import networkx as nx
import nodegen
import threading
import socket
import select
import time
from NodeObj import NodeObj

def rerouter(node_obj):
    time.sleep(60)
    while True:
        if (node_obj.reroute_flag):
            print("Testing?")
            node_obj.reroute_flag = False
            nodegen.routing_table(node_obj.G,node_obj.node)




# Create a server and listen for incoming connections from neighbouring ports.
def create_server_and_listen(node_obj):
    
    host_port = node_obj.server_port
    
    
    print("Server hosted on port {}".format(host_port))
    expected_connections = len(node_obj.neighbour_ports)
    host = node_obj.host
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # solution for "[Error 89] Address already in use". Use before bind()
    s.bind((host, host_port))
    s.listen(expected_connections) # Number of connections is the number of neighbours in the graph.

    sockets = node_obj.server_sockets

    # Connect to all clients that are trying to connect. Number of connections expected is the number of neighbours.
    try:
        while len(sockets) != expected_connections:
            print("Waiting for client")
            conn, addr = s.accept()
            sockets.append(conn)

            print("Client:", addr)
            
    except KeyboardInterrupt:
        print("Stopped by Ctrl+C")
    
    # Listen to messages forever. 
    while True:
        # Select returns ready sockets that have informaiton in them.
        if sockets:
            ready_socks,_,_ = select.select(sockets, [], []) 

            for sock in ready_socks:
                    data = sock.recv(3000) 
                    if not data:
                        sock.close()
                        sockets.remove(sock)

                    # Decode messages recieved.
                    else: 
                        message = node_obj.decode_topology(data)
                        print(f"Received message:",message)




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
                print(f"Connection established to {port}")

            except Exception as e:
                print(f"Failed connecting to {port}: {e}")
                time.sleep(3)

    while True:
        # Get all new links. Designed in a way such that we never miss information.
        for sock in node_obj.client_sockets:
            try:
                sock.send(node_obj.encode_topology())
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




    