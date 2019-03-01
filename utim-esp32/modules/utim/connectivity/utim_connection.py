"""
Utim Connection module

This module implements Utim connection and messaging through the MQTT or AMQP
"""

import utime as time
import logging
import queue
import _thread
import event
from ..utilities import connmanager, config
import ubinascii

logger = logging.Logger('connectivity.top.uhost.utim_connection')


class UtimConnectionException(Exception):
    """
    Exception of UtimConnection
    """

    pass


class UtimConnectionInvalidDataException(UtimConnectionException):
    """
    UtimConnection invalid data exception
    """

    pass


class UtimConnection(object):
    """
    MQTT class
    """

    def __init__(self, topic, name, type):
        """
        Initialize MQTT connection
        """

        self.__inbound_queue = queue.Queue()  # Queue for inbound data
        self.__outbound_queue = queue.Queue()  # Queue for outbound data
        self.__topic = topic
        self.__utim_name = name
        self.__type = type
        self.__client = None

        # Threads
        self.__run2_thread = None

        # Run event
        self.__run_event = event.Event()

        self.__config = config.Config()

    def connect(self):
        """
        Establish connection
        :return:
        """

        self.__client = connmanager.ConnManager(self.__type)

    def stop(self):
        """
        Stop
        """

        if self.__client:
            self.__client.disconnect()

        if self.__run_event:
            self.__run_event.clear()

        if self.__run2_thread:
            self.__run2_thread.exit()

    def run(self):
        """
        Run subscribe and publish to MQTT-broker
        """

        logger.info("Try to run in another thread")
        self.__run_event.set()

        logger.info('Starting THREAD_UTIM_CONNECTION_RUN')
        self.__run2_thread = _thread.start_new_thread(
            self.__run2,
            ()
        )
        # name='THREAD_UTIM_CONNECTION_RUN'
        # self.__run2_thread.daemon = True
        # self.__run2_thread.start()

    def __run2(self):
        """
        Run listening and writing to Serial port
        Use it in another thread.
        """

        # Subscribe to topic
        self.__client.subscribe(self.__topic, self, self._on_message)
        logger.debug("Subscribed to topic: {}".format(self.__topic))

        logger.info("Start Running")
        while self.__run_event.is_set():
            self.__publish()
            time.sleep(1)

        logger.info("Stopping processing..")

    def __publish(self):
        """
        Publish
        """

        while not self.__outbound_queue.empty():
            try:
                message = self.__outbound_queue.get_nowait()
                logger.debug("Publish item: {}".format(message))

                destination = ubinascii.unhexlify(self.__config.uhost_name)
                logger.debug("Message: {}".format(message))
                logger.debug("Type message: {}".format(type(message)))
                self.__client.publish(self.__utim_name.encode(), destination.decode(), message)
                logger.debug("Message {} was published to {}".format(
                    str(destination),
                    str(message)))

            except queue.Empty:
                pass

    def _on_message(self, conn, sender, message):
        """
        Message receiving callback

        :param sender: Message sender
        :param message: The message

        Author: kanphis@gmail.com
        Created: 16.08.2017
        Edited: 16.08.2017
        """
        # This log message causes the thing to crash because of the stack overflow =__=
        # logger.info("Received message {0} from {1}".format(message, sender))
        while not self.__put_data(message):
            pass

    def __put_data(self, data):
        """
        Put data

        :param data:
        :return bool:
        """

        try:
            self.__inbound_queue.put_nowait(data)
        except queue.Full:
            return False

        return True

    def receive(self):
        """
        Receive method

        :param TopDataType data_type: Top data type
        :return bytes|None: Data
        """

        try:
            return self.__inbound_queue.get_nowait()
        except queue.Empty:
            pass

        return None

    def send(self, data):
        """
        Send method

        :param bytes data: Data to send
        :return bool: True if data is sent, False - otherwise
        :raise: UtimConnectionInvalidDataException
        """

        if isinstance(data, bytes):
            try:
                self.__outbound_queue.put_nowait(data)
                return True

            except queue.Full:
                pass

            return False

        else:
            raise UtimConnectionInvalidDataException()
