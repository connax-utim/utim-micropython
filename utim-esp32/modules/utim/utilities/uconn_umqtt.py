"""
UConnUMQTT module

This module implements the MQTT connection and messaging through the Mosquitto broker
"""

import logging
import _thread
import utim.utilities.config as _config
import utim.utilities.exceptions as exceptions
from umqtt.simple import MQTTClient

logger = logging.Logger('utilities.uconn_umqtt')


class MQTTThreadException(Exception):
    pass


class UConnUMQTT(object):
    """
    UMQTT class
    """

    def __init__(self):
        """
        Initialize MQTT connection
        """

        self.__topic = None
        self.__message_callback = None

        self.thread_going = False
        self.thread = None

        # Get connection parameters
        username, password, host = self.__get_connection_parameters()

        # Establish connection
        self.__establish_connection(username, password, host)

    @staticmethod
    def __log_exception(ex):
        """
        Exception handler
        :param ex: Raised exception
        :raise: UtimConnectionException, UtimUnknownException
        """

        etype = type(ex)

        if etype == ValueError and \
                (str(ex) == 'Invalid host.' or str(ex) == 'Invalid credentials.'):
            logger.debug("Connection error " + str(ex))
            raise exceptions.UtimConnectionException
        if etype == exceptions.UtimExchangeException:
            print("Exchange error " + str(ex))
            logger.debug("Exchange error " + str(ex))
            raise exceptions.UtimExchangeException
        else:
            logger.debug('Unknown error ' + str(ex))
            raise exceptions.UtimUnknownException

    @staticmethod
    def __get_connection_parameters():
        """
        Function to get parameters for Mosquitto broker from config.py
        :return: Triplet of username, password and host address
        :rtype: str, str, str
        """
        config = _config.Config()
        return config.mqtt['user'], config.mqtt['pass'], config.mqtt['host']

    def __establish_connection(self, username, password, hostname):
        """
        Exception handler
        :param str username: User name
        :param str password: User password
        :param str hostname: Host name
        :return: Opened channel
        :raise: UtimConnectionException
        """

        try:
            if username is None or password is None:
                raise ValueError('Invalid credentials.')
            if hostname is None:
                raise ValueError('Invalid host.')

            # Parameters and credentials
            self.__client = MQTTClient("umqtt_client", hostname, user=username, password=password)
            self.__client.set_callback(self._on_message)
            self.__client.connect()
            self.loop_start()
        except ValueError:
            raise exceptions.UtimConnectionException

    def disconnect(self):
        """
        Disconnect from broker
        """
        self.loop_stop()
        self.__client.disconnect()

    def subscribe(self, topic, cbobj, callback):
        """
        Subscribe
        :param str topic: Channel name to listen
        :param callback: Callback
        """
        self.__topic = topic
        self.__cbobject = cbobj
        self.__message_callback = callback
        self.__client.subscribe(topic)

    def listen(self):
        self.__client.check_msg()

    def unsubscribe(self, topic):
        """
        Unsubscribe
        :param str topic: Channel name to listen
        """

        self.__topic = None
        self.__cbobject = None
        self.__message_callback = None

    def publish(self, sender, destination, message):
        """
        Publish
        :param str sender: Message sender
        :param str destination: Message destination (non empty string)
        :param str message: The message to send
        """
        try:
            if (not isinstance(destination, str) or not destination or
                    not isinstance(message, bytes) or
                    not isinstance(sender, bytes)):
                raise exceptions.UtimExchangeException
            msg = sender + b' ' + message
            self.__client.publish(destination.encode(), msg)
        except exceptions.UtimExchangeException as ex:
            self.__log_exception(ex)

    def _on_message(self, userdata, msg):
        """
        On message callback
        :param userdata: private user data as set in Client() or userdata_set()
        :param message: instance of MQTTMessage
        :returns: 0 - if custom message callback was called,
                  1 - if custom message callback is None,
                  None - else
        """
        m = msg.partition(b' ')
        if callable(self.__message_callback):
            self.__message_callback(self.__cbobject, m[0], m[2])
            return 0
        return 1

    def loop(self):
        while self.thread_going:
            self.listen()

    def loop_start(self):
        self.thread_going = True
        logger.info('Starting THREAD_UMQTT_LOOP')
        self.thread = _thread.start_new_thread(self.loop, ())

    def loop_stop(self):
        # if self.thread is None:
        #     raise MQTTThreadException
        self.thread_going = False
        if self.thread is not None:
            self.thread.exit()
