import multiprocessing
import os
import asyncio
import logging
import socket
from my_http import Request, Response, Methods
from pathlib import Path
import time


def getFds(pid):
    return os.listdir('/proc/%s/fd/' % pid)


def getPos(pid, fd):
    with open('/proc/%s/fdinfo/%s' % (pid, fd)) as f:
        return int(f.readline()[5:])


class Worker(multiprocessing.Process):
    def __init__(self, sock: socket.socket):
        super(Worker, self).__init__()
        self.sock = sock
        # self.loop = asyncio.new_event_loop()
        self.loop = None

    def run(self):
        self.loop = asyncio.get_event_loop()

        info(self.name)

        self.loop.set_debug(True)
        print(asyncio.get_event_loop_policy())
        print(self.loop)
        print('')

        print(self.sock.fileno())
        print(getFds(os.getpid()))
        print(getPos(os.getpid(), self.sock.fileno()))
        # for x in getFds(os.getpid()):
        #     print(os.fstat(int(x)))


        try:
            self.loop.run_until_complete(self.work())
        except KeyboardInterrupt as e:
            print("Caught keyboard interrupt. Canceling tasks...")
            # logging.info("Process interrupted")
        finally:
            # logging.info("Successfully shutdown worker.")
            print('Successfully shutdown worker.')
            self.loop.close()

    async def work(self):
        while True:
            conn, _ = await self.loop.sock_accept(self.sock)
            info("WORK " + self.name)
            print("")
            conn.settimeout(10)
            conn.setblocking(False)
            self.loop.create_task(self.handle_conn(conn))

            # await asyncio.sleep(10)

    async def handle_conn(self, conn):
        if self.name == "Worker-1":
            time.sleep(100)
        req_data = await self.loop.sock_recv(conn, 1000)

        info("HANDLE_CONN " + self.name)
        print("")

        # response = b'HTTP/1.1 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
        # response += b'my-key: my-value\r\n'

        req = Request(req_data.decode())
        res = Response()

        dir_index = 'index.html'
        DOCUMENT_ROOT = '.'
        res_p = None


        if req.method == Methods.Get or req.method == Methods.Head:
            if req.path.endswith('/'):
                req.path += dir_index

            p = Path(DOCUMENT_ROOT)
            p = Path(str(p) + req.path)
            res_p = p
            data = ''
            if p.exists() and p.is_file():
                with p.open('rb') as f:
                    data = f.read()
                    res.set_body(data, req.path)
            else:
                res.status = 404
        else:
            res.status = 405

        print(res.parse_http())
        response = res.parse_http()

        await self.loop.sock_sendall(conn, response)

        # if res_p.exists() and res_p.is_file():
        #     with res_p.open('rb') as ff:
        #         await self.loop.sock_sendfile(conn, ff)

        conn.close()

    async def hanle(self):
        pass



def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())
