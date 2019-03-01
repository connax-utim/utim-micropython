"""
Subprocessor for device messages
"""
import logging
from ..utilities.tag import Tag
from ..workers import device_worker_forward
from ..workers import device_worker_startup
from ..utilities.address import Address
from ..utilities.status import Status
from ..utilities.data_indexes import SubprocessorIndex

_SubprocessorIndex = SubprocessorIndex()

logger = logging.Logger('utilities.process_device')


class ProcessDevice(object):
    """
    Subprocessor for device messages
    """

    def __init__(self, utim):
        """
        Initialization of subprocessor for device messages
        """

        self.__utim = utim

    def process(self, data):
        """
        Process device message
        :param data: array [source, destination, status, body]
        :return: same as input
        """
        logger.info('Starting device processing')
        # Placeholder for data being processed, that will be returned one day
        res = data

        while (res[_SubprocessorIndex.status] is not Status.STATUS_TO_SEND and
               res[_SubprocessorIndex.status] is not Status.STATUS_FINALIZED and
               res[_SubprocessorIndex.source] is Address.ADDRESS_DEVICE):
            command = res[_SubprocessorIndex.body][0:1]
            if command == Tag.INBOUND.DATA_TO_PLATFORM:
                res = device_worker_forward.process(self.__utim, res)
            elif command == Tag.INBOUND.NETWORK_READY:
                res = device_worker_startup.process(self.__utim, res)
            else:
                res[_SubprocessorIndex.status] = Status.STATUS_FINALIZED

            if (res[_SubprocessorIndex.status] is Status.STATUS_TO_SEND or
                    res[_SubprocessorIndex.status] is Status.STATUS_FINALIZED):
                break
        return res
