import os


def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())


def getFds(pid):
    return os.listdir('/proc/%s/fd/' % pid)


def getPos(pid, fd):
    with open('/proc/%s/fdinfo/%s' % (pid, fd)) as f:
        return int(f.readline()[5:])
