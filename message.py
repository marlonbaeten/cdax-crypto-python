from M2Crypto import RSA, EVP, Rand
from utilities import config

# encryption options:
# des_ede_ecb, des_ede_cbc, des_ede_cfb, des_ede_ofb,
# des_ede3_ecb, des_ede3_cbc, des_ede3_cfb, des_ede3_ofb,
# aes_128_ecb, aes_128_cbc, aes_128_cfb, aes_128_ofb,
# aes_192_ecb, aes_192_cbc, aes_192_cfb, aes_192_ofb,
# aes_256_ecb, aes_256_cbc, aes_256_cfb, aes_256_ofb
# not recommended:
# bf_ecb, bf_cbc, bf_cfb, bf_ofb,
# idea_ecb, idea_cbc, idea_cfb, idea_ofb,
# cast5_ecb, cast5_cbc, cast5_cfb, cast5_ofb,
# rc5_ecb, rc5_cbc, rc5_cfb, rc5_ofb,
# des_ecb, des_cbc, des_cfb, des_ofb,
# rc4, rc2_40_cbc

class Message:
    ''' all messages are send in this format over TCP '''

    def __init__(self, identity, topic, data):
        # identity of the message publisher
        self.identity = identity
        # topic name string
        self.topic = topic
        # encrypted or signed message data
        self.data = data
        # signature of mac
        self.auth = None
        # unencrypted message data
        self.metadata = {
            # mac or signature algorithm
            'auth_algo': config.crypto['hmac']['hash'],
            # symmetric encryption algorithm
            'enc_algo': config.crypto['encryption']['algo'],
            # encryption initialization vector
            'iv': None,
        }
        # time stamp of message publication
        self.timestamp = None

    def sign_rsa(self, key):
        ''' add RSA signature to message '''
        self.auth = key.sign(self.data)

    def verify_rsa(self, key):
        ''' verify the RSA signature on the message '''
        return key.verify(self.data, self.auth)

    def encrypt_rsa(self, key):
        ''' encrypt the message using the RSA public key '''
        self.data = key.public_encrypt(self.data, RSA.pkcs1_padding)

    def decrypt_rsa(self, key):
        ''' decrypt the message using the RSA private key '''
        self.data = key.private_decrypt(self.data, RSA.pkcs1_padding)

    def sign(self, key):
        ''' sign the message using HMAC '''
        hmac = EVP.HMAC(key, self.metadata['auth_algo'])
        hmac.update(self.data)
        self.auth = hmac.digest()

    def verify(self, key):
        ''' verify the HMAC of the message '''
        hmac = EVP.HMAC(key, self.metadata['auth_algo'])
        hmac.update(self.data)
        return self.auth == hmac.digest()

    def encrypt(self, key):
        ''' encrypt the message using the specified symmetric algorithm '''
        self.metadata['iv'] = Rand.rand_bytes(16)
        self._symmetric(key)

    def decrypt(self, key):
        ''' decrypt the message using the specified symmetric algorithm '''
        self._symmetric(key, 0)

    def _symmetric(self, key, mode = 1):
        ''' perform ymmetric encryption or decryption based on the mode '''
        cipher = EVP.Cipher(
            alg = self.metadata['enc_algo'],
            key = key,
            iv = self.metadata['iv'],
            op = mode
        )
        v = cipher.update(self.data)
        self.data = v + cipher.final()


# module unit-test
if __name__ == '__main__':
    msg = Message('foo', 'bar', 'message')
    key1 = Rand.rand_bytes(16)
    key2 = Rand.rand_bytes(16)
    print msg.data
    msg.encrypt(key1)
    msg.sign(key2)
    print msg.auth
    print msg.data
    print msg.verify(key2)
    msg.decrypt(key1)
    print msg.data
