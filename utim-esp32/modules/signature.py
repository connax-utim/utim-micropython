# from uhashlib import sha256
# import hmac
import chmac


class Signature(object):

    @staticmethod
    def create_signature(secret_key, message):
        message_to_sign = message.encode('utf-8')
        # sha256 by default, hardcoded into chmac
        hashed = chmac.hmac(secret_key, len(secret_key), message_to_sign, len(message_to_sign))
        return hashed.hexdigest()

    def message_sign(self, key, message):
        hmac = self.create_signature(key, message)
        signature = message + " " + hmac
        return signature

    def authenticate_signed_token(self, signed_message, key):
        message, signature = signed_message.rsplit(" ", 1)
        our_token = self.message_sign(key, message).rsplit(" ", 1)[-1]
        return True if signature == our_token else False
