import threading
import time

from M2Crypto import RSA, Rand
from utilities import config
from client import Publisher, Subscriber
from node import Node
from secserver import SecServer

def create_rsa_keypair():
    settings = config.crypto['rsa']
    return RSA.gen_key(settings['keylength'], settings['exponent'], lambda: None)

def create_topic_keypair():
    return {
        'encryption': Rand.rand_bytes(16),
        'authentication': Rand.rand_bytes(16)
    }

def main():

    topic_keys = {}

    for topic in config.topics:
        topic_keys[topic] = create_topic_keypair()

    nodes = []

    for identity in config.nodes:
        node = Node(identity)
        node.setPort(config.nodes[identity]['port'])
        for topic in config.nodes[identity]['topics']:
            node.addTopicKey(topic, topic_keys[topic]['authentication'])
        nodes.append(node)

    client_keys = {}
    clients = []

    # create client administration and generate keypairs
    for identity in config.clients:
        client_keys[identity] = create_rsa_keypair()

        if config.clients[identity]['type'] == 'publisher':
            client = Publisher(identity, client_keys[identity])
        elif  config.clients[identity]['type'] == 'subscriber':
            client = Subscriber(identity, client_keys[identity])
            client.setPort(config.clients[identity]['port'])

        client.setAllowedTopics(config.clients[identity]['allowed_topics'])
        clients.append(client)

    secserver = SecServer(client_keys, topic_keys)

    secserver.start()

    for node in nodes:
        node.start()

    for client in clients:
        client.start()

    return (secserver, clients, nodes)

def stop(secserver, clients, nodes):

    secserver.serve = False

    for node in nodes:
        node.serve = False

    for client in clients:
        client.serve = False


if __name__ == '__main__':
    try:
        (secserver, clients, nodes) = main()
        while threading.active_count() > 0:
            time.sleep(1)
    except KeyboardInterrupt:
        stop(secserver, clients, nodes)
    except:
        print "Simulation finished..."
        stop(secserver, clients, nodes)
