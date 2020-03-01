import select
import socket
from my_http import Request, Response, Methods
from pathlib import Path


EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
response = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
response += b'Hello, world!'

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(('0.0.0.0', 8080))
serversocket.listen(100)
serversocket.setblocking(0)

epoll = select.epoll()
epoll.register(serversocket.fileno(), select.EPOLLIN)

try:
    connections = {}
    requests = {}
    responses = {}
    while True:
        events = epoll.poll(1)
        for fileno, event in events:
            if fileno == serversocket.fileno():
                connection, address = serversocket.accept()
                connection.setblocking(0)
                epoll.register(connection.fileno(), select.EPOLLIN)
                connections[connection.fileno()] = connection
                requests[connection.fileno()] = b''
                responses[connection.fileno()] = response
            elif event & select.EPOLLIN:
                requests[fileno] += connections[fileno].recv(1024)
                if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
                    epoll.modify(fileno, select.EPOLLOUT)
                    print('-' * 40 + '\n' + requests[fileno].decode()[:-2])

                    req = Request(requests[fileno].decode())
                    res = Response()

                    dir_index = '../src/index.html'
                    DOCUMENT_ROOT = '.'
                    # DOCUMENT_ROOT = '/var/www/html'

                    if req.method == Methods.Get or req.method == Methods.Head:
                        if req.path.endswith('/'):
                            req.path += dir_index

                        p = Path(DOCUMENT_ROOT)
                        p = Path(str(p) + req.path)
                        data = ''
                        if p.exists() and p.is_file():
                            with p.open('rb') as f:
                                data = f.read()
                                res.set_body(data, req.path)
                        else:
                            # res.set_body(b'Not found\r\n', 'a.txt')
                            res.status = 404
                    else:
                        # res.set_body(b'Not allowed\r\n', 'a.txt')
                        res.status = 405

                    print(res.parse_http())
                    responses[fileno] = res.parse_http()
            elif event & select.EPOLLOUT:
                byteswritten = connections[fileno].send(responses[fileno])

                responses[fileno] = responses[fileno][byteswritten:]
                if len(responses[fileno]) == 0:
                    epoll.modify(fileno, 0)
                    connections[fileno].shutdown(socket.SHUT_RDWR)
            elif event & select.EPOLLHUP:
                epoll.unregister(fileno)
                connections[fileno].close()
                del connections[fileno]
finally:
    epoll.unregister(serversocket.fileno())
    epoll.close()
    serversocket.close()
