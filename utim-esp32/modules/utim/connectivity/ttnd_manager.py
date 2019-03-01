import logging
import queue
import _thread
import event
from . import utim_connection
from ..utilities.exceptions import *
from .utim_connection import UtimConnectionInvalidDataException

logger = logging.Logger('connectivity.ttnd_manager')


class DataType(object):
    """
    List of types of data to process
    """

    DEVICE = 0
    UHOST = 1
    PLATFORM = 2

    @classmethod
    def validate(cls, data_type):
        """

        :param data_type:
        :return bool: True - if data_type is valid, False - otherwise
        """

        # Check type of input data type
        if isinstance(data_type, int):
            if data_type in [cls.DEVICE, cls.UHOST, cls.PLATFORM]:
                return True

        return False


class ManagerConnectionStatus(object):
    """
    List of Top Manager statuses
    """

    # General
    NOT_INITIALIZED = -1        # Connection is not initialized
    SUCCESS = 0                 # Everything is ok
    INVALID_CONFIG = 1          # Config file does not consist required key
    INVALID_HOST = 2            # Host is not to __connection
    INVALID_CREDENTIALS = 3     # Auth error
    UNKNOWN_PLATFORM_TYPE = 4   # Unknown platform type to create connection

    # Azure
    AZURE_ERROR = 10                  # General Azure error
    AZURE_UNKNOWN_AUTH_METHOD = 11    # Unknown auth method
    AZURE_NO_CONNECTION_STRING = 12   # Can not create connection string

    # Azure
    AWS_ERROR = 20                  # General AWS error
    AWS_UNKNOWN_AUTH_METHOD = 21    # Unknown auth method
    AWS_NO_CONNECTION_STRING = 22   # Can not create connection string

    # Uhost
    UHOST_ERROR = 30                # General Uhost error
    UHOST_CONNECTION_ERROR = 31     # Connection error

    # Device
    DEVICE_ERROR = 90   # General Device error


class Manager(object):

    def __init__(self, **kwargs):
        self.__uhost_connection = None
        self.__uhost_status = None

        # Threads
        self.__inbound_thread = None
        self.__outbound_thread = None

        # Run event
        self.__run_event = event.Event()

        # Queues
        self.__inbound_queue = queue.Queue()
        self.__outbound_queue = queue.Queue()
        self.__device_queue = queue.Queue()
        self.__uhost_queue = queue.Queue()
        self.__platform_queue = queue.Queue()
        self.__tx = None
        self.__rx = None

        self.connect(**kwargs)

        # Run processing
        self.__run_event.set()

        logger.info("process_inbound starting..")
        self.__run_process_inbound()
        logger.info("process_outbound starting..")
        self.__run_process_outbound()

    # Datalink connection
    def connect(self, **kwargs):
        if 'tx' not in kwargs.keys() or 'rx' not in kwargs.keys():
            raise DataLinkRealisationWrongArgsException()
        if not isinstance(kwargs['tx'], queue.Queue) or not isinstance(kwargs['rx'], queue.Queue):
            raise DataLinkRealisationWrongArgsException()
        self.__tx = kwargs['tx']
        self.__rx = kwargs['rx']

    def __run_process_inbound(self):
        """
        Run inbound data processing in another thread
        """

        self.__inbound_thread = _thread.start_new_thread(
            self.__process_inbound,
            ()
        )

    def __run_process_outbound(self):
        """
        Run outbound data processing in another thread
        """

        self.__outbound_thread = _thread.start_new_thread(
            self.__process_outbound,
            ()
        )

    def __process_inbound(self):
        """
        Process inbound data queue in loop
        """

        while self.__run_event.is_set():
            data_device = self.__process_inbound_transport()
            if data_device is not None:
                while not self.__put_data([DataType.DEVICE, data_device]):
                    pass

            if (self.__uhost_connection and
                    self.__uhost_status == ManagerConnectionStatus.SUCCESS):
                data_uhost = self.__uhost_connection.receive()
                if data_uhost is not None:
                    while not self.__put_data([DataType.UHOST, data_uhost]):
                        pass

    def __process_inbound_transport(self):
        # DataType.DEVICE by default
        data = self.__process_inbound_network()
        if data is not None:
            # Data must be bytes type
            if isinstance(data, bytes):
                # Data must be 3 bytes at a minimum
                data_length = len(data)
                if data_length >= 3:
                    tag_bytes = data[0:1]
                    tag = int.from_bytes(tag_bytes, 'big')
                    length_bytes = data[1:3]
                    length = int.from_bytes(length_bytes, 'big')
                    data = data[3:3 + length]
                    if DataType.validate(tag) is True:
                        # while not self.__put_data(data):
                        #     pass
                        return data
                    else:
                        logger.debug("Unknown data type - {}: {}".format(tag, str(data)))

                else:
                    logger.debug("Invalid data length - {}: {}".format(data_length, str(data)))

            else:
                logger.error("Invalid data type: {}".format(str(data)))

        return None

    def __process_inbound_network(self):
        data = self.__process_inbound_datalink()
        if data is not None:
            # Data must be bytes type
            if isinstance(data, bytes):
                # Data must be 3 bytes at a minimum
                data_length = len(data)
                if data_length >= 3:
                    tag_bytes = data[0:1]
                    tag = int.from_bytes(tag_bytes, 'big')
                    length_bytes = data[1:3]
                    length = int.from_bytes(length_bytes, 'big')
                    data = data[3:3+length]

                    if tag == DataType.DEVICE:
                        return data

                    else:
                        logger.debug("Unknown data type - {}: {}".format(tag, str(data)))
                else:
                    logger.debug("Invalid data length - {}: {}".format(data_length, str(data)))

            else:
                logger.error("Invalid data type: {}".format(str(data)))

        return None

    def __process_inbound_datalink(self):
        if self.__rx is None:
            raise DataLinkRealisationConnectionException()

        try:
            return self.__rx.get_nowait()

        except queue.Empty:
            pass

        return None

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

    def __process_outbound(self):
        """
        Process outbound data queue
        """

        while self.__run_event.is_set():
            try:
                data = self.__outbound_queue.get_nowait()
                logger.debug('Sending data: {}'.format(data))
                data_type = data[0]
                data = data[1]
                if DataType.validate(data_type):
                    try:
                        if (data_type == DataType.DEVICE):
                            self.__process_outbound_transport(data_type, data)
                        elif (data_type == DataType.UHOST and
                              self.__uhost_status == ManagerConnectionStatus.SUCCESS):
                            while not self.__uhost_connection.send(data):
                                pass
                        else:
                            logger.debug("Manager has no active status connections !")

                    except UtimConnectionInvalidDataException:
                        pass
                    except UtimDeviceInvalidDataException:
                        pass
                else:
                    logger.debug("Unknown data type - {}: {}".format(data_type, str(data)))

            except queue.Empty:
                pass

        logger.info("Stopping outbound processing..")

    def __process_outbound_transport(self, destination, data):
        logger.debug('Transport Send data {}'.format(data))
        try:
            # Assemble packet
            dest = destination.to_bytes(1, 'big')
            length = len(data).to_bytes(2, 'big')
            packet = dest + length + data

            # sending to DEVICE by default
            tag = DataType.DEVICE
            self.__process_outbound_network(tag, packet)

        except queue.Empty:
            pass

    def __process_outbound_network(self, destination, data):
        logger.debug('Network Send data {}'.format(data))
        if DataType.validate(destination):
            if isinstance(data, bytes):
                length = len(data).to_bytes(2, 'big')
                dest = destination.to_bytes(1, 'big')
                packet = dest + length + data
                self.__process_outbound_datalink(packet)

    def __process_outbound_datalink(self, message):
        logger.debug('Datalink Send data {}'.format(message))
        if type(message) is not bytes:
            raise DataLinkRealisationWrongArgsException()
        if self.__tx is None:
            raise DataLinkRealisationConnectionException()

        try:
            self.__tx.put_nowait(message)

        except queue.Full:
            return False

        return True

    def receive(self):
        """
        Receive method

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

        :return bool: True if data is sent, False - otherwise
        :raises: ManagerDataTypeException
        """
        logger.debug('Top Send data {}'.format(data))
        data_type = data[0]
        if DataType.validate(data_type):
            try:
                self.__outbound_queue.put_nowait(data)
                return True

            except queue.Full:
                pass

            return False

        else:
            raise ManagerDataTypeException()

    def run_uhost_connection(self, config):
        """
        Run uhost connection in another thread

        :param dict config: Config of uhost connection
        """

        try:
            # Get values
            topic = config['topic']
            name = config['name']
            protocol = config['protocol']

            # Establish connection
            self.__uhost_connection = utim_connection.UtimConnection(
                topic,
                name,
                protocol
            )
            self.__uhost_connection.connect()
            self.__uhost_connection.run()

            # Return result

            self.__uhost_status = ManagerConnectionStatus.SUCCESS

        except KeyError:
            logger.error('Invalid config file: {}'.format(config))
            self.__uhost_status = ManagerConnectionStatus.INVALID_CONFIG

        except UtimConnectionException:
            logger.error('Utim connection exception')
            self.__uhost_status = ManagerConnectionStatus.UHOST_CONNECTION_ERROR

        except UtimUnknownException:
            logger.error('Utim unknown exception')
            self.__uhost_status = ManagerConnectionStatus.UHOST_ERROR

        return self.__uhost_status

    def stop(self):
        """
        Stop
        """

        if self.__run_event:
            self.__run_event.clear()

        if self.__inbound_thread:
            self.__inbound_thread.exit()
        if self.__outbound_thread:
            self.__outbound_thread.exit()
