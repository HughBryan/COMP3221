
import sys
import networkx as nx
import nodegen
import threading
import socket
import select
import time

# Create a server and listen for incoming connections from neighbouring ports.
def create_server_and_listen(host_port,neighbour_ports,Graph):

    print("Server hosted on port {}".format(host_port))
    num_connections = len(neighbour_ports)
    host = '127.0.0.1'
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # solution for "[Error 89] Address already in use". Use before bind()
    s.bind((host, host_port))
    s.listen(num_connections) # Number of connections is the number of neighbours in the graph.

    sockets = []

    # Connect to all clients that are trying to connect. Number of connections expected is the number of neighbours.
    try:
        while len(sockets) != num_connections:
            print("Waiting for client")
            conn, addr = s.accept()
            sockets.append(conn)

            print("Client:", addr)
            print(f"Connections: {sockets}")
            
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
                        print(f"Received message:", data.decode("utf-8"))



# Establish connections with neighbours. 
def establish_connections(ports,Graph):
    sockets = []
    host = "127.0.0.1"

    for port in ports:

        connected = False
        while not connected:    
            try:
                s = socket.socket(socket.AF_INET,socket.SOCK_STREAM,)
                s.connect((host,port))
                sockets.append(s)
                connected = True
                print(f"Connection established to {port}")

            except Exception as e:
                print(f"Failed connecting to {port}: {e}")
                time.sleep(3)

    for sock in sockets:
        sock.send(str(f"sending_msg_to_{sock.getsockname()[1]}").encode("utf-8"))







#python COMP3221_A1_Routing.py F 6005 Fconfig.txt

if __name__ == "__main__":
    # Startup. Get commandline arguments etc.

    if (len(sys.argv) < 4):
        raise Exception("Insufficient Command-Line Arguments")

    node = sys.argv[1]
    port_number = int(sys.argv[2])
    config = sys.argv[3]

    # Initiate Node graph.
    G = nx.Graph()
    G.add_node(node,port = port_number)

    try:
        with open(config,"r") as file:
            lines = int(file.readline())
            for i in range(0,lines):
                line = file.readline().strip().split()
                G.add_node(line[0],port = int(line[2]))
                G.add_edge(node,line[0],weight =round(float(line[1]),1))

    except:
        raise Exception("Invalid config file")


    neighbour_ports = [int(G.nodes()[node]['port']) for node in G.neighbors(node)]


    # Listening Thread / Server thread
    listen_thread = threading.Thread(target=create_server_and_listen,args=(port_number,neighbour_ports,G))
    listen_thread.start()

    # Sending thread
    sending_thread = threading.Thread(target = establish_connections,args = (neighbour_ports,G))
    sending_thread.start()
    # Routing Calculation thread




    