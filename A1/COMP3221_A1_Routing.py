
import sys
import networkx as nx
import nodegen

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

    # Listening Thread
    # Sending thread
    # Routing Calculation thread
    