import sys
import yaml
import time
import random

class Config:
    ''' class that holds the system configuration'''

    # internal dictionary
    _values = None

    def __init__(self):
        # read configuration file
        self._values = yaml.load(open('config.yml', 'r'))

    def __getattr__(self, name):
        ''' overload attribute get method '''
        if self._values.has_key(name):
            return self._values[name]
        else:
            raise AttributeError

# read config file to make the configuration accesible
config = Config()

class Color:
    ''' terminal colors '''

    blue   = '\033[94m'
    green  = '\033[92m'
    orange = '\033[93m'
    red    = '\033[91m'


def log(identity, msg, *args):
    ''' log a colored message to the terminal '''
    if identity[0:3] == 'pub':
        color = Color.green
    elif identity[0:3] == 'sub':
        color = Color.orange
    elif identity[0:4] == 'node':
        color = Color.blue
    else:
        color = Color.red
    # format identity string
    identity = '> %s' % identity
    identity = identity.ljust(15)
    # format message string
    msg = msg % args
    # output formatted message
    sys.stdout.write('%s%s\033[0m %s\n' % (color, identity, msg))

def wait():
    ''' wait an arbitrary amount of time '''
    time.sleep(2 + random.random() * 2)
