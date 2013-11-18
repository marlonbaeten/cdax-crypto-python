import random

from message import Message
from network import Network
from utilities import log, config, wait

class Client(Network):
    ''' abstract C-DAX client '''

    def __init__(self, identity, keypair):
        # call parent constructor (the network thread)
        super(Client, self).__init__()
        # name of the client
        self.identity = identity
        # RSA key-pair of the client
        self.keypair = keypair
        # flag used to stop the thread nicely
        self.serve = True
        # dictionary to store topic keys
        self.topics = {}

    def setAllowedTopics(self, topics):
        ''' set a list of allowed topic names '''
        self.allowed_topics = topics

    def joinTopic(self, topic):
        ''' send join topic request to the security server '''
        log(self.identity, 'request join for "%s"', topic)
        request = Message(self.identity, topic, 'topic_join')
        # sign the request
        request.sign_rsa(self.keypair)
        # send the request to the topic node
        response = self.send(self.lookup(topic), request)
        # decrypt the response
        if response:
            response.decrypt_rsa(self.keypair)
            # check for the presence of topic keys
            if response.data:
                # extract topic keys
                self.topics[topic] = {
                    'encryption':     response.data[0:16],
                    'authentication': response.data[16:32]
                }
                log(self.identity, 'received keys for "%s"', topic)

class Publisher(Client):
    ''' publisher C-DAX client '''

    # shared message counter
    message_counter = 0

    def createRandomMessage(self):
        ''' create a random message on one of the available topics '''
        topic = random.choice(self.topics.keys())
        data = 'message_%d' % self.message_counter
        self.message_counter += 1
        message = Message(self.identity, topic, data)
        return message

    def sendMessage(self, message):
        ''' send topic message to the correct node '''
        port = self.lookup(message.topic)
        log(self.identity, 'sent "%s" to "%s"', message.data, message.topic)
        topic_keys = self.topics[message.topic]
        # encrypt-than-sign message
        message.encrypt(topic_keys['encryption'])
        message.sign(topic_keys['authentication'])
        self.send(port, message)

    def run(self):
        ''' main thread loop, send messages in regular interval'''
        while self.serve:
            # wait a random amount of time
            wait()
            # request a topic key if not all topic keys are received yet
            if len(self.topics) < len(self.allowed_topics):
                topic = self.allowed_topics[len(self.topics)]
                self.joinTopic(topic)
            else:
                # send a random message to a random topic
                self.sendMessage(self.createRandomMessage())


class Subscriber(Client):
    ''' subscriber C-DAX client '''

    def setPort(self, port):
        ''' set the port number to listen to '''
        self.port = port

    def handle(self, conn, message):
        ''' handle a new TCP message '''
        topic_keys = self.topics[message.topic]
        # check the HMAC using the correct topic key
        if message.verify(topic_keys['authentication']):
            # decrypt the message using the correct topic key
            message.decrypt(topic_keys['encryption'])
            log(self.identity, 'received  "%s" from "%s"', message.data, message.identity)

    def hartbeat(self):
        ''' hart-beat called in the main server loop '''
        if len(self.topics) < len(self.allowed_topics):
            # wait a random amount of time
            wait()
            # request a topic key if not all topic keys are received yet
            topic = self.allowed_topics[len(self.topics)]
            self.joinTopic(topic)
