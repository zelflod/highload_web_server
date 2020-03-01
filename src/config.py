import configparser
import argparse


class Config:
    section = 'dummy_section'
    config = configparser.ConfigParser(inline_comment_prefixes='#', delimiters=' ')
    host = '0.0.0.0'
    port = 8085
    max_waiting_conns = 5
    recv_buf_size = 1024
    conn_timeout = 10
    dir_index = 'index.html'

    def init(self, conf_path):
        with open(conf_path, 'r') as f:
            config_string = '[{}]\n'.format(self.section) + f.read()
        self.config.read_string(config_string)

    @property
    def cpu_limit(self):
        return self.config.getint(self.section, 'cpu_limit')

    @property
    def thread_limit(self):
        return self.config.getint(self.section, 'thread_limit')

    @property
    def document_root(self):
        return self.config.get(self.section, 'document_root')

    @property
    def address(self):
        return self.host, self.port


def get_conf_path():
    conf_path = 'httpd.conf'
    parser = argparse.ArgumentParser()
    parser.add_argument('--httpd_conf')
    args = parser.parse_args()
    conf_path = conf_path if args.httpd_conf is None else args.httpd_conf

    return conf_path
