import mimetypes
from email.utils import formatdate
from datetime import datetime
from time import mktime
from enum import Enum


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

dir_index = 'index.html'
DOCUMENT_ROOT = '?'

headers = {
    'Server': 'python_non_blocking_server',
    'Date': '',
    'Connection': '',
    'Content-Length': '',
    'Content-Type': ''
}


def guess_mime_type(filename):
    print('guess_mime_type', filename)
    return mimetypes.guess_type(filename)


# print(guess_mime_type('some.js'))


def process_request():
    print("handle_request")


class Response:
    headers = {}
    path = ''
    body = b''
    response_version = 'HTTP/1.1'
    status = 200
    date = ''
    content_type = ''
    content_length = ''

    def __init__(self):
        self.status = 200
        self.closed = False

    def read(self):
        print('read')

    def parse_http(self):
        res = '{} {} {}\r\n'.format(self.response_version, self.status, STATUS_CODES[self.status])
        res += 'Date: {}\r\n'.format(get_now_datetime())
        res += 'Server: {}\r\n'.format('not_nginx')
        res += 'Connection: {}\r\n'.format('close')
        if self.body:
            res += 'Content-Type: {}\r\n'.format(self.content_type)
            res += 'Content-Length: {}\r\n'.format(self.content_length)
            res += '\r\n'
        res_bytes = bytes(res, 'utf8')
        res_bytes += self.body

        return res_bytes

    def set_body(self, data, filename):
        # self.body = bytes(data, 'utf8')
        self.body = data
        # self.content_type = 'text/plain'
        self.content_type = guess_mime_type(filename)[0]
        self.content_length = len(self.body)


class Request:
    def __init__(self, request_text):
        request_line, headers_alone = request_text.split('\r\n', 1)
        self.method, self.path, self.request_version = request_line.split(' ')

        self.headers = {}
        for h in headers_alone.split('\r\n'):
            h = h.split(':', 1)
            if len(h) == 2:
                self.headers[h[0]] = h[1]


class HTTPConnection:
    # https: // docs.python.org / 3.6 / library / http.client.html  # httpconnection-objects
    request = {}

    def __init__(self):
        print('http connection')
