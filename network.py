import pickle
import socket
import threading

from utilities import log, config

# default socket timeout
socket.setdefaulttimeout(30)

class Network(threading.Thread):
    ''' basic TCP server '''

    def __init__(self):
        # init thread
        threading.Thread.__init__(self)

    def send(self, connection, message):
        ''' send a message over TPC to the specified port or connection '''
        # encode the message class
        content = pickle.dumps(message)
        # check for port number or connection instance
        if not isinstance(connection, int):
            soc = connection
        else:
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # try to connect, return when the connection fails
            try:
                soc.connect((config.network['ip'], connection))
            except:
                log(self.identity, 'could not connect to port %d', connection)
                return False
        # send a message over the socket connection
        soc.send(content)
        response = soc.recv(config.network['buffer_size'])
        # when a response is present, decode the message class
        if response:
            response = pickle.loads(response)
        # close the TCP connection
        soc.close()
        return response

    def run(self):
        ''' execute the main thread loop '''
        if not self.port:
            # do not act as a server when there is no port number specified
            return
        # set-up TCP server on specified port and address
        log(self.identity, 'listening on port %d', self.port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((config.network['ip'], self.port))
        s.listen(config.network['connections'])
        # main server loop
        while self.serve:
            # call hart-beat callback periodically
            self.hartbeat()
            # wait for a new connection, this will fail after x seconds
            try:
                conn, addr = s.accept()
            except:
                continue
            # receive TCP message
            data = conn.recv(config.network['buffer_size'])
            # decode message instance
            message = pickle.loads(data)
            # call handle method
            self.handle(conn, message)
            conn.close()
        # close the port when server terminates
        s.close()

    def hartbeat(self):
        ''' hart-beat called in the main server loop '''
        pass

    def lookup(self, topic):
        ''' lookup node port number given a topic name '''
        node = config.topics[topic]['node']
        return config.nodes[node]['port']



