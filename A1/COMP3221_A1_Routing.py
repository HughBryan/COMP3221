
import sys
import networkx as nx
import nodegen
import threading
import socket
import time

def listening_thread(conn, addr):
    print("listening starting")

    # recv message
    message = conn.recv(1024)
    message = message.decode()
    print("listening from port:", addr, 'recv:', message)
    return

def sending_thread(conn, addr):  
    # send answer
    return


if __name__ == "__main__":
    #python COMP3221_A1_Routing.py F 6005 Fconfig.txt
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


    nodegen.display_graph(G,False)
    host = '0.0.0.0'
    port = 6000
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # solution for "[Error 89] Address already in use". Use before bind()
    s.bind((host, port))
    s.listen(1)

    try:
        while True:
            print("Waiting for client")
            conn, addr = s.accept()
    
            print("Client:", addr)

            # Listening Thread
            listen = threading.Thread(target=listening_thread, args=(conn, addr))
            listen.start()

            # Sending thread
            send = threading.Thread(target=listening_thread, args=(conn, addr))
            send.start()
                    
            # Routing Calculation thread

    except KeyboardInterrupt:
        print("Stopped by Ctrl+C")
    
    conn.close()

"""     while True:
        for neighbour in G.nodes.items():
            try:
                while True:
                    print("Waiting for client")
                    conn, addr = s.accept()
    
                    print("Client:", addr)

                    # Listening Thread
                    listen = threading.Thread(target=listening_thread, args=(conn, addr))
                    listen.start()

                    # Sending thread
                    send = threading.Thread(target=listening_thread, args=(conn, addr))
                    send.start()

                    # Routing Calculation thread

            except KeyboardInterrupt:
                print("Stopped by Ctrl+C")
    
            conn.close() """






    



