"""ConnManager containing script"""
import logging
from .connmanagermqtt import ConnManagerMQTT
from .uconn_umqtt import UConnUMQTT as UConnMQTT

logger = logging.Logger('utilities.connmanager')


class ConnManager(object):
    """
    Wrapper around connections. Be free to choose anything you want!
    MQTT. Your choise is limited
    """

    CONNECTION_TYPE_MQTT = 'mqtt'
    CONNECTION_TYPE_UMQTT = 'umqtt'

    def __init__(self, connection_type):
        """
        Initialization of ConnManager

        :param str connection_type: Connection type (mqtt)
        """
        logger.info('Initializing ConnManager, type: ' + connection_type)
        if connection_type == ConnManager.CONNECTION_TYPE_MQTT:
            self.__connection = ConnManagerMQTT()
        else:
            self.__connection = UConnMQTT()

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
        :param object callback_object: Object with callback method
        :param method callback: Callback for received message
        """
        logger.info("Subscribing for {0}".format(topic))
        self.__callback_object = callback_object
        self.__callback = callback
        self.__connection.subscribe(topic, self, ConnManager._on_message)

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
        logger.info("Publishing {} to topic {}".format(message, destination))
        self.__connection.publish(sender, destination, message)

    def _on_message(self, sender, message):
        """
        Message receiving callback

        :param sender: Message sender
        :param message: The message
        """
        logger.info("Received message {} from {}".format(message, sender))
        self.__callback(self.__callback_object, sender, message)
