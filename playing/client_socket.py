import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 8000))
s.sendall(b'Hello world!')

bufsize = 4096

data = s.recv(bufsize)
s.close()
print("Полученные данные: ", repr(data))
