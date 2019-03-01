"""
Process Item module
"""

import logging
import queue
import _thread
import event
from .address import Address
from .status import Status
from . import process_device
from . import process_uhost
from . import process_platform
from .data_indexes import ProcessorIndex, SubprocessorIndex

_ProcessorIndex = ProcessorIndex()
_SubprocessorIndex = SubprocessorIndex()

logger = logging.Logger('utilities.process_item')


class ProcessItemException(Exception):
    """
    General ProcessItemException
    """

    pass


class InputParametersException(ProcessItemException):
    """
    Input parameters exception
    """

    pass


class ProcessItem(object):
    """
    Process Item class
    """

    def __init__(self, utim, in_queue, out_queue):
        """
        Initialization

        :param Utim utim: Utim instance
        :param Queue in_queue: Inbound queue
        :param Queue out_queue: Outbound queue
        """

        # Check input parameters
        if not (isinstance(in_queue, queue.Queue) and isinstance(out_queue, queue.Queue)):
            raise InputParametersException()

        # Set utim
        self.__utim = utim

        # Threads
        self.__run_thread = None

        # Run event
        self.__run_event = event.Event()

        # Queues
        self.__inbound_queue = in_queue
        self.__outbound_queue = out_queue

        # Handlers
        self.__device = process_device.ProcessDevice(self.__utim)
        self.__uhost = process_uhost.ProcessUhost(self.__utim)
        self.__platform = process_platform.ProcessPlatform(self.__utim)

        logger.info("Process Item is initialized!")

    def __process(self, data):
        """
        Inbound data processing and

        :param list data: Data to process [Source, Body]
        :return list: Processed data
        """

        source = data[_ProcessorIndex.address]
        destination = Address.ADDRESS_UTIM
        status = Status.STATUS_PROCESS
        body = data[_ProcessorIndex.body]

        # [From, To, Status, Message]
        data_to_process = [source, destination, status, body]

        address = source
        while data_to_process[_SubprocessorIndex.status] not in\
                (Status.STATUS_TO_SEND, Status.STATUS_FINALIZED):
            if address == Address.ADDRESS_DEVICE:
                data_to_process = self.__device.process(data_to_process)

            elif address == Address.ADDRESS_UHOST:
                data_to_process = self.__uhost.process(data_to_process)

            elif address == Address.ADDRESS_PLATFORM:
                data_to_process = self.__platform.process(data_to_process)

            if isinstance(data_to_process, list) and len(data_to_process) == 4:
                if (data_to_process[_SubprocessorIndex.source] == Address.ADDRESS_UTIM and
                        data_to_process[_SubprocessorIndex.destination] != Address.ADDRESS_UTIM):
                    address = data_to_process[_SubprocessorIndex.destination]

                elif (data_to_process[_SubprocessorIndex.source] != Address.ADDRESS_UTIM and
                      data_to_process[_SubprocessorIndex.destination] == Address.ADDRESS_UTIM):
                    address = data_to_process[_SubprocessorIndex.source]

                else:
                    data_to_process = self.__error_handler(data_to_process)

            else:
                break

        # print("Data PROCESSED", data_to_process)
        return self.__return_item(data_to_process)

    def __return_item(self, data):
        """
        Assemble answer

        :param data: Data
        :return list|None:
        """

        if isinstance(data, list) and len(data) == 4:
            if (data[_SubprocessorIndex.destination] is not Address.ADDRESS_UTIM and
                    data[_SubprocessorIndex.status] is not Status.STATUS_FINALIZED):
                return [
                    data[_SubprocessorIndex.destination],
                    data[_SubprocessorIndex.body]
                ]

        if data is not None:
            logger.error("Invalid data to return: {} {}".format(type(data), str(data)))

        return None

    def run(self):
        """
        Run
        """

        self.__run_event.set()

        logger.info('Starting THREAD_PROCESS_ITEM_RUN')
        self.__run_thread = _thread.start_new_thread(
            self.__run2,
            ()
        )
        # name='THREAD_PROCESS_ITEM_RUN'
        # self.__run_thread.daemon = True
        # self.__run_thread.start()

    def __run2(self):
        """
        Run2
        """

        while self.__run_event.is_set():
            # print('(. Y .)')
            try:
                data = self.__inbound_queue.get_nowait()
                res = self.__process(data)
                if res:
                    while not self.__put_data(res):
                        pass
            except queue.Empty:
                pass

        logger.info("Stopping processing..")

    def __put_data(self, data):
        """
        Put data

        :param data:
        :return bool:
        """

        try:
            self.__outbound_queue.put_nowait(data)
        except queue.Full:
            return False

        return True

    def stop(self):
        """
        Stop
        """

        if self.__run_event:
            self.__run_event.clear()

        if self.__run_thread:
            self.__run_thread.exit()

    def __error_handler(self, data):
        """
        Error handler

        :param data: Data
        """

        logger.error("Item processing error: {}".format(str(data)))

        if isinstance(data, list) and len(data) == 4:
            data[_SubprocessorIndex.status] = Status.STATUS_FINALIZED
            return data

        return None
