import asyncio
import socket
import os


def print_data(conn):
    print(conn.recv(1000))


response = b'HTTP/1.1 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
response += b'my-key: my-value\r\n'
# response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
# response += b'Hello, world!'


async def main(loop, response):
    sock = socket.socket()
    # привязываем к локалхосту на 8086 порту
    sock.bind(('localhost', 8085))
    sock.listen(100)
    sock.setblocking(False)
    # добавляем коллбэк для чтения данных
    # loop.add_reader(sock, print_data)

    while True:
        conn, _ = await loop.sock_accept(sock)
        conn.settimeout(10)
        conn.setblocking(False)
        # loop.create_task(self.handle_client(conn))
        data = await loop.sock_recv(conn, 1000)
        print(data)
        await loop.sock_sendall(conn, response)
        # filename = 'index.html'
        filename = 'async_server.py'
        with open(filename, 'rb') as f:
            file_len = os.path.getsize(filename)
            response += b'Content-Type: text/plain\r\nContent-Length: '
            print(bytes(str(file_len), 'utf-8'))
            response += bytes(str(file_len), 'utf-8')
            response += b'\r\n\r\n'
            print(response)
            await loop.sock_sendall(conn, response)
            print('with')
            await loop.sock_sendfile(conn, f)
        conn.close()


loop = asyncio.get_event_loop()
# loop.call_soon(main, loop)
# loop.run_forever()
# loop.sock_accept()
loop.run_until_complete(main(loop, response))
loop.close()
