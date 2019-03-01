"""ConnManagerMQTT containing script"""
import _thread
import utime as time
import random
import logging
from .uconn_umqtt import UConnUMQTT as UConnMQTT
from . import exceptions

logger = logging.Logger('utilities.connmanagermqtt')


class ConnManagerMQTT(object):
    """
    UconnMQTT wrapper that guarantee delivery to addressee
    """

    _SENDER = 'sender'
    _DESTINATION = 'destination'
    _MESSAGE = 'message'

    def __init__(self):
        """
        Initialization of ConnManager
        """
        logger.info('Initializing ConnmanagerMQTT')
        self.__connection = UConnMQTT()
        self.__message_number = random.randint(0, 65536)
        self.__sent_messages = dict()
        self.__callback = None
        self.__callback_object = None

    def disconnect(self):
        """
        Disconnection from server
        """
        logger.info('Disconnecting...')
        self.__connection.disconnect()

    def subscribe(self, topic, callback_object, callback):
        """
        Subscribe on topic

        :param str topic: Topic for subscription
        :param method callback: Callback for received message
        """
        logger.info("Subscribing for {0}".format(topic))
        if not callable(callback):
            raise exceptions.UtimUncallableCallbackError
        self.__callback = callback
        self.__callback_object = callback_object
        self.__connection.subscribe(topic, self, ConnManagerMQTT._on_message)

    def unsubscribe(self, topic):
        """
        Unsubscribe from topic

        :param str topic: Topic for subscription cancelling
        """
        logger.info("Unsubscribing from {0}".format(topic))
        self.__connection.unsubscribe(topic)

    def publish(self, sender, destination, message):
        """
        Publish message

        :param sender: Message sender
        :param destination: Message destination
        :param message: The message
        """
        id = self.__message_number
        self.__message_number = (self.__message_number + 1) % 65536
        out_message = b'\x01' + id.to_bytes(2, 'big') + message
        logger.info("Publishing {} to topic {}".format(message, destination))
        self.__connection.publish(sender, destination, out_message)
        self.__sent_messages[id] = {self._SENDER: sender,
                                    self._DESTINATION: destination,
                                    self._MESSAGE: message}

        logger.info('Starting THREAD_PUBLISH')
        _thread.start_new_thread(self._republish, (id,))

    def _republish(self, id):
        """
        Check if message was delivered and republish if not

        :param id: Message ID
        """
        logger.info("_publish for {0} started".format(id))
        time.sleep(10)
        while id in self.__sent_messages.keys():
            try:
                logger.info("Message {0} wasn\'t delivered".format(id))
                message = self.__sent_messages[id]
                self.__connection.publish(message[self._SENDER], message[self._DESTINATION],
                                          b'\x01' + id.to_bytes(2, 'big') + message[self._MESSAGE])
                time.sleep(5)
            except KeyError:
                logger.error("Message was already deleted from republish")
                break

        logger.info("Message {0} was delivered".format(id))

    def _on_message(self, sender, message):
        """
        Message receiving callback

        :param sender: Message sender
        :param message: The message
        """
        logger.info("Received message {0} from {1}".format(message, sender))
        if len(message) < 3:
            logger.info('Message is too short to be something!')
        else:
            if message[:1] == b'\x02':
                try:
                    logger.info('Received ack, deleting message from sent')
                    id = int.from_bytes(message[1:3], 'big')
                    if id in self.__sent_messages.keys():
                        self.__sent_messages.pop(id)
                except KeyError:
                    logger.error("Message was already deleted from republish")
            else:
                logger.info('Received message, sending ack...')
                ack_message = b'\x02' + message[1:3]
                self.__connection.publish(b'ack', sender.decode(), ack_message)
                self.__callback(self.__callback_object, sender, message[3:])
