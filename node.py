from network import Network
from utilities import log, config

class Node(Network):
    ''' C-DAX node representation '''

    def __init__(self, identity):
        super(Node, self).__init__()
        # node name
        self.identity = identity
        # flag used to stop the server thread nicely
        self.serve = True
        # dictionary of subscribers per-topic
        self.subscribers = {}
        # dictionary of topic authentication keys
        self.topic_keys = {}

    def setPort(self, port):
        ''' set the port number of this node '''
        self.port = port

    def addTopicKey(self, topic, key):
        ''' add a topic/authentication key to this node '''
        self.topic_keys[topic] = key

    def handle(self, conn, message):
        ''' TCP server callback '''
        if message.data == 'topic_join':
            # forward topic join requests to the security server
            response = self.send(config.server['port'], message)
            # add subscriber to the topic subscriber list when the response is positive
            if response and config.clients[message.identity]['type'] == 'subscriber':
                if message.topic not in self.subscribers:
                    self.subscribers[message.topic] = [message.identity]
                else:
                    self.subscribers[message.topic].append(message.identity)
            # return server response to the client
            self.send(conn, response)
        elif message.verify(self.topic_keys[message.topic]):
            # forward ligitimate topic data to list of subscribers
            log(self.identity, 'received message on "%s" from "%s"', message.topic, message.identity)
            self.publish(message)

    def publish(self, message):
        ''' public topic data to list of subscribers '''
        if message.topic in self.subscribers:
            subscribers = self.subscribers[message.topic]
            log(self.identity, 'forwarded message to %d subscribers', len(subscribers))
            for identity in subscribers:
                self.send(config.clients[identity]['port'], message)



