# https://docs.python.org/3.6/howto/sockets.html#socket-howto

import socket
import select

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# s.setblocking(False)

# HOST = 'localhost'
HOST = socket.gethostname()
PORT = 8000
s.bind((HOST, PORT))
s.listen(5)

# while True:
#     (clientsocket, address) = s.accept()
#     ct = client_thread(clientsocket)
#     ct.run()

epo = select.epoll()
epo.register(s)

conn, addr = s.accept()

bufsize = 4096

with conn:
    print('Connected by', addr)
    while True:
        data = conn.recv(bufsize)
        if not data: break
        conn.sendall(data)
    # s.sendfile()
conn.close()

# class MySocket:
