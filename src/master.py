from worker import Worker, getFds, getPos
from config import Config, get_conf_path
import socket
import os
import multiprocessing

# multiprocessing.allow_connection_pickling()


def main(config):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 8086))
    sock.listen(100)
    sock.setblocking(False)
    print("Running server")

    print(getFds(os.getpid()))
    print(getPos(os.getpid(), sock.fileno()))
    print(os.fstat(sock.fileno()))

    # multiprocessing.set_start_method("fork")

    workers = []
    for x in range(config.cpu_limit):
        w = Worker(sock)
        workers.append(w)
        w.start()

    try:
        for w in workers:
            w.join()
    except KeyboardInterrupt:
        for w in workers:
            w.terminate()
    finally:
        sock.close()


if __name__ == "__main__":
    config_path = get_conf_path()
    conf = Config()
    conf.init(config_path)

    main(conf)
