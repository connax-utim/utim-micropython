"""Cryptography layer for Utim and Uhost"""

from ucryptolib import aes
import chmac
import logging
from .tag import Tag

logger = logging.Logger('utilities.cryptography')


class CryptoLayer(object):
    """
    Cryptography layer object
    """

    SIGN_MODE_NONE = b'\x00'
    SIGN_MODE_SHA256 = b'\x01'

    CRYPTO_MODE_NONE = b'\x00'
    CRYPTO_MODE_AES = b'\x01'

    UCRYPTOLIB_MODE_CBC = 2

    __SIGN_SHA256_LENGTH = 32
    __iv = b'\x75\xbe\x38\x2b\x42\x51\xc7\x05\xa2\x43\x23\x5d\xe0\xf4\xb5\x08'

    def __init__(self, key):
        """
        Initialization of CryptoLayer
        For AES key must be 16, 24 or 32 bytes
        """
        logger.info('Creating new layer with key {}'.format(key))
        self.__key = key

    @staticmethod
    def is_secured(message):
        """
        Is message secured
        """
        if message[0:1] == Tag.CRYPTO.ENCRYPTED:
            if message[1:2] != CryptoLayer.CRYPTO_MODE_NONE:
                return True
        elif message[0:1] == Tag.CRYPTO.SIGNED:
            if message[1:2] != CryptoLayer.SIGN_MODE_NONE:
                return True
        return False

    def encrypt(self, mode, message):
        """
        Encrypt message
        """
        if self.__key is not None and mode != self.CRYPTO_MODE_NONE:
            if mode == self.CRYPTO_MODE_AES:
                cipher = aes(self.__key, self.UCRYPTOLIB_MODE_CBC, self.__iv)
                if(len(message) % 16 > 0):
                    message += (b' ' * (16 - len(message) % 16))
                return Tag.CRYPTO.ENCRYPTED + mode + cipher.encrypt(message)
        return Tag.CRYPTO.ENCRYPTED + self.CRYPTO_MODE_NONE + message

    def decrypt(self, message):
        """
        Decrypt message
        """
        if len(message) < 2:
            return None
        if self.__key is None:
            if message[1:2] == self.CRYPTO_MODE_NONE:
                return message[2:]
        elif message[1:2] == self.CRYPTO_MODE_AES:
            cipher = aes(self.__key, self.UCRYPTOLIB_MODE_CBC, self.__iv)
            return cipher.decrypt(self.__iv + message[2:])[16:]
        return None

    def sign(self, mode, message):
        """
        Sign message
        """
        if self.__key is not None and mode != self.SIGN_MODE_NONE:
            logger.debug('Signing mode', mode)
            if mode == self.SIGN_MODE_SHA256:
                # sha256 hardcoded into chmac
                signature = chmac.hmac(self.__key, len(self.__key), message, len(message))
                return Tag.CRYPTO.SIGNED + mode + message + signature
        return Tag.CRYPTO.SIGNED + self.SIGN_MODE_NONE + message

    def unsign(self, message):
        """
        Unsign message
        """
        if len(message) < 2:
            return None
        if self.__key is None:
            if message[1:2] == self.SIGN_MODE_NONE:
                return message[2:]
        elif message[1:2] == self.SIGN_MODE_SHA256:
            # message end is full length minus signature length
            message_end = len(message) - self.__SIGN_SHA256_LENGTH
            useful_message = message[2:message_end]
            signature = message[message_end:]
            ref_signature = chmac.hmac(self.__key, len(self.__key),
                                       useful_message, len(useful_message))
            if signature == ref_signature:
                return useful_message
        return None
