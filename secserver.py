from utilities import config, log
from network import Network
from message import Message

class SecServer(Network):
    ''' C-DAX security server representation '''

    # server name
    identity = 'sec_server'

    def __init__(self, client_keys, topic_keys):
        super(SecServer, self).__init__()
        # keypairs of all clients in the system
        self.client_keys = client_keys
        # topic keys for all topics in the system
        self.topic_keys = topic_keys
        # port of this server
        self.port = config.server['port']
        # flag used to stop the thread nicely
        self.serve = True

    def handle(self, conn, request):
        ''' TCP server callback '''
        if request.data == 'topic_join':
            # handle topic join requests
            log(self.identity, 'received join request from "%s" for "%s"', request.identity, request.topic)
            client_key = self.client_keys[request.identity]
            # check signature of the request
            if request.verify_rsa(client_key):
                # retrieve topic keys and concatenate before encrypting
                topic_key = self.topic_keys[request.topic]
                content = topic_key['encryption'] + topic_key['authentication']
                # send back response encrypted with client public key
                response = Message(self.identity, request.topic, content)
                response.encrypt_rsa(client_key)
                self.send(conn, response)
