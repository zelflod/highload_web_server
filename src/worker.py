import multiprocessing
import os
import asyncio
import socket
from my_http import Request, Response, Methods
from pathlib import Path
import time
import urllib.parse


def getFds(pid):
    return os.listdir('/proc/%s/fd/' % pid)


def getPos(pid, fd):
    with open('/proc/%s/fdinfo/%s' % (pid, fd)) as f:
        return int(f.readline()[5:])


class Worker(multiprocessing.Process):
    def __init__(self, sock, config):
        super(Worker, self).__init__()
        self.sock = sock
        self.loop = None
        self.config = config

    def run(self):
        self.loop = asyncio.get_event_loop()

        info(self.name)

        # self.loop.set_debug(True)
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
        finally:
            print('Successfully shutdown worker.')
            self.loop.close()

    async def work(self):
        while True:
            conn, _ = await self.loop.sock_accept(self.sock)
            # info("WORK " + self.name)
            # print("")
            conn.settimeout(self.config.conn_timeout)
            conn.setblocking(False)
            self.loop.create_task(self.handle_conn(conn))

    async def handle_conn(self, conn):
        req_data = await self.loop.sock_recv(conn, self.config.recv_buf_size)

        # info("HANDLE_CONN " + self.name)
        # print("")

        req = Request(req_data.decode())
        res = Response(conn, self.loop)

        self.loop.create_task(self.handle(req, res))

    async def handle(self, req, res):
        # print(req.method, req.path)

        if req.method != Methods.Get and req.method != Methods.Head:
            res.status = 405
            response = res.parse_http()
            await res.send(response)
            return res.end()

        path = urllib.parse.unquote(req.path)

        if req.path.endswith('/'):
            path += self.config.dir_index

        p = Path(self.config.document_root)
        path = str(p) + path
        p = Path(path)

        norm_path = os.path.normpath(path)
        if norm_path[:len(self.config.document_root)] != self.config.document_root:
            res.status = 403
            response = res.parse_http()
            await res.send(response)
            return res.end()

        if not p.exists() or not p.is_file():
            if req.path.endswith('/'):
                res.status = 403
            else:
                res.status = 404
            response = res.parse_http()
            await res.send(response)
            return res.end()

        with p.open('rb') as f:
            res.set_body("has body", path)
            response = res.parse_http(False)
            await res.send(response)
            if req.method != Methods.Head:
                await res.send_file(f)
            res.end()

        # if req.method == Methods.Get or req.method == Methods.Head:
        #     path = urllib.parse.unquote(req.path)
        #
        #     if req.path.endswith('/'):
        #         path += self.config.dir_index
        #
        #     p = Path(self.config.document_root)
        #     p = Path(str(p) + path)
        #
        #     norm_path = os.path.normpath(str(p) + path)
        #     if norm_path[:len(self.config.document_root)] != self.config.document_root:
        #         res.status = 403
        #     else:
        #         res_p = p
        #         data = ''
        #         if p.exists() and p.is_file():
        #             with p.open('rb') as f:
        #                 data = f.read()
        #                 res.set_body(data, path)
        #         else:
        #             if req.path.endswith('/'):
        #                 res.status = 403
        #             else:
        #                 res.status = 404
        # else:
        #     res.status = 405

        # print(res.status, res.path)
        # include_body = True if req.method != Methods.Head else False
        # response = res.parse_http(include_body)
        #
        # # await self.loop.sock_sendall(conn, response)
        # await res.send(response)
        #
        # # if res_p.exists() and res_p.is_file():
        # #     with res_p.open('rb') as ff:
        # #         await self.loop.sock_sendfile(conn, ff)
        #
        # # conn.close()
        # res.end()


def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())
