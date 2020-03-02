import multiprocessing
import os
import asyncio
from my_http import Request, Response, Methods
from pathlib import Path
import urllib.parse


class Worker(multiprocessing.Process):
    def __init__(self, sock, config):
        super(Worker, self).__init__()
        self.sock = sock
        self.loop = None
        self.config = config

    def run(self):
        self.loop = asyncio.get_event_loop()

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
            conn.settimeout(self.config.conn_timeout)
            conn.setblocking(False)
            self.loop.create_task(self.handle_conn(conn))

    async def handle_conn(self, conn):
        req_data = await self.loop.sock_recv(conn, self.config.recv_buf_size)

        req = Request(req_data.decode())
        res = Response(conn, self.loop)

        res, include_body = self.handle(req, res)

        response = res.get_http_headers()
        await res.send(response)

        if include_body:
            with res.body_filepath.open('rb') as f:
                await res.send_file(f)
        res.end()

    def handle(self, req, res):
        if req.method != Methods.Get and req.method != Methods.Head:
            res.status = 405
            return res, False

        path = urllib.parse.unquote(req.path)

        if req.path.endswith('/'):
            path += self.config.dir_index

        p = Path(self.config.document_root)
        path = str(p) + path
        p = Path(path)

        norm_path = os.path.normpath(path)
        if norm_path[:len(self.config.document_root)] != self.config.document_root:
            res.status = 403
            return res, False

        if not p.exists() or not p.is_file():
            if req.path.endswith('/'):
                res.status = 403
            else:
                res.status = 404
            return res, False

        include_body = False if req.method == Methods.Head else True
        res.set_body_headers(p, path)
        return res, include_body
