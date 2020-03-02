import mimetypes
from email.utils import formatdate
from datetime import datetime
from time import mktime
import os


class Methods:
    Get = 'GET'
    Head = 'HEAD'


def get_now_datetime():
    now = datetime.now()
    stamp = mktime(now.timetuple())
    return formatdate(
        timeval=stamp,
        localtime=False,
        usegmt=True
    )


MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.swf': 'application/x-shockwave-flash',
}

STATUS_CODES = {
    200: 'OK',
    403: 'FORBIDDEN',
    404: 'NOT_FOUND',
    405: 'METHOD_NOT_ALLOWED'
}

allowed_methods = ['GET', 'HEAD']

headers = {
    'Server': 'python_non_blocking_server',
    'Date': '',
    'Connection': '',
    'Content-Length': '',
    'Content-Type': ''
}


def guess_mime_type(filename):
    return mimetypes.guess_type(filename)


class Response:
    headers = {}
    path = ''
    response_version = 'HTTP/1.1'
    status = 200
    date = ''
    content_type = ''
    content_length = ''
    body_filepath = None

    def __init__(self, conn, loop):
        self.status = 200
        self.closed = False
        self.conn = conn
        self.loop = loop

    def get_http_headers(self, include_body=True):
        res = '{} {} {}\r\n'.format(self.response_version, self.status, STATUS_CODES[self.status])
        res += 'Date: {}\r\n'.format(get_now_datetime())
        res += 'Server: {}\r\n'.format('not_nginx')
        res += 'Connection: {}\r\n'.format('close')
        if self.body_filepath:
            res += 'Content-Type: {}\r\n'.format(self.content_type)
            res += 'Content-Length: {}\r\n'.format(self.content_length)
            res += '\r\n'
        res_bytes = bytes(res, 'utf8')

        return res_bytes

    def set_body_headers(self, data, filename):
        self.body_filepath = data
        self.content_type = guess_mime_type(filename)[0]
        with open(filename, 'rb') as f:
            file_len = os.path.getsize(filename)
            self.content_length = str(file_len)

    async def send(self, data):
        await self.loop.sock_sendall(self.conn, data)

    async def send_file(self, file):
        try:
            await self.loop.sock_sendfile(self.conn, file)
        except IOError as e:
            pass

    def end(self):
        self.conn.close()


class Request:
    def __init__(self, request_text):
        self.method = ""
        self.path = ""
        self.request_version = ""
        self.headers = {}

        try:
            request_line, headers_text = request_text.split('\r\n', 1)
            self.method, path_string, self.request_version = request_line.split(' ')
        except:
            return

        try:
            self.path, query_params = path_string.split('?')
        except ValueError:
            self.path = path_string

        for h in headers_text.split('\r\n'):
            h = h.split(':', 1)
            if len(h) == 2:
                self.headers[h[0]] = h[1]
