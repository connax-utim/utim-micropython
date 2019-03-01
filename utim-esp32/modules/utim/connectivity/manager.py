import logging
from . import ttnd_manager as manager

logger = logging.Logger('connectivity.manager')


class ConnectivityException(Exception):
    """
    General connectivity exception
    """

    pass


class ConnectivityWrongArgsException(ConnectivityException):
    """
    Wrong arguments
    """

    pass


class ConnectivityConnectError(ConnectivityException):
    """
    Connection error
    """

    pass


class ConnectivityManager(object):
    """
    Connectivity manager class
    """

    def __init__(self, **kwargs):
        """
        Initialization
        """
        self.__manager = None
        self.connect(**kwargs)

    def connect(self, **kwargs):
        """

        :param dl_type: DataLink manager connection type
        :param tx: Queue to transmit data
        :param rx: Queue to receive data
        :return:
        """

        self.__manager = manager.Manager(**kwargs)


    def send(self, data):
        """
        Send method

        :param data: Data to send
        :return bool:
        """

        return self.__manager.send(data)

    def receive(self):
        """
        Receive method

        :return:
        """

        return self.__manager.receive()

    def run_uhost_connection(self, config):
        """
        Run Uhost connection

        :param dict config: Config
        :return:
        """

        return self.__manager.run_uhost_connection(config)

    def stop(self):
        """
        Stop
        """

        if self.__manager:
            self.__manager.stop()
