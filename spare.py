import socket
def func():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # solution for "[Error 89] Address already in use". Use before bind()
    s.bind(("127.0.0.1", 6000))
    s.listen(1) # Number of connections is the number of neighbours in the graph.
    conn,adr = s.accpet()

def func2():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM,)
    s.connect(("127.0.0.1",6000))
    sock.send("test".encode('utf7'))