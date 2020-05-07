from pathlib import Path
import datetime

LOG_FILE = Path('./log.txt')

def makeTimeStamped():
    fmt='%m-%d %H:%M:%S'
    return datetime.datetime.now().strftime(fmt)

def log(func):
    def wrapper(*args, **kw):
        _time = makeTimeStamped()
        with open(LOG_FILE, 'a+') as p:
            p.write('%s  call %s \n' %(_time, func.__name__))
        return func(*args, **kw)
    return wrapper