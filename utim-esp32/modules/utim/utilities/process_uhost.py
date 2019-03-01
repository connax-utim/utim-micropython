"""
Subprocessor for uhost messages
"""

import logging
from ..utilities.tag import Tag
from ..workers import utim_worker_try
from ..workers import utim_worker_init
from ..workers import utim_worker_connection_string
from ..workers import utim_worker_error
from ..workers import utim_worker_platform_verify
from ..workers import utim_worker_authentic
from ..workers import utim_worker_encrypt
from ..workers import utim_worker_decrypt
from ..workers import utim_worker_sign
from ..workers import utim_worker_unsign
from ..workers import utim_worker_keepalive
from ..utilities.data_indexes import SubprocessorIndex
from ..utilities.address import Address
from ..utilities.status import Status

_SubprocessorIndex = SubprocessorIndex()

logger = logging.Logger('utilities.process_uhost')


class ProcessUhost(object):
    """
    Subprocessor for uhost messages
    """

    def __init__(self, utim):
        """
        Initialization of subprocessor for uhost messages
        """

        self.__utim = utim

    def process(self, data):
        """
        Process uhost message
        :param data: array [source, destination, status
        :return: same as input
        """

        res = data

        logger.info('Data to decipher:       {}'.format(res))

        if (res[_SubprocessorIndex.source] is Address.ADDRESS_UHOST and
                res[_SubprocessorIndex.status] is Status.STATUS_PROCESS):
            res = utim_worker_unsign.process(self.__utim, res)
        if (res[_SubprocessorIndex.source] is Address.ADDRESS_UHOST and
                res[_SubprocessorIndex.status] is Status.STATUS_PROCESS):
            res = utim_worker_decrypt.process(self.__utim, res)

        logger.info('Data after deciphering: {}'.format(res))

        while (res[_SubprocessorIndex.status] is not Status.STATUS_TO_SEND and
               res[_SubprocessorIndex.status] is not Status.STATUS_FINALIZED and
               res[_SubprocessorIndex.source] is Address.ADDRESS_UHOST):
            command = res[_SubprocessorIndex.body][0:1]
            if command == Tag.UCOMMAND.TRY_FIRST:
                res = utim_worker_try.process(self.__utim, res)
            elif command == Tag.UCOMMAND.INIT:
                res = utim_worker_init.process(self.__utim, res)
            elif command == Tag.UCOMMAND.CONNECTION_STRING:
                res = utim_worker_connection_string.process(self.__utim, res)
            elif command == Tag.UCOMMAND.TEST_PLATFORM_DATA:
                res = utim_worker_platform_verify.process(self.__utim, res)
            elif command == Tag.UCOMMAND.AUTHENTIC:
                res = utim_worker_authentic.process(self.__utim, res)
            elif command == Tag.UCOMMAND.ERROR:
                res = utim_worker_error.process(self.__utim, res)

            elif command == Tag.UCOMMAND.KEEPALIVE:
                res = utim_worker_keepalive.process(self.__utim, res)

            else:
                res[_SubprocessorIndex.status] = Status.STATUS_FINALIZED

        if (res[_SubprocessorIndex.destination] == Address.ADDRESS_UHOST
                and res[_SubprocessorIndex.status] == Status.STATUS_PROCESS):
            res = utim_worker_encrypt.process(self.__utim, res)
            res = utim_worker_sign.process(self.__utim, res)

        return res
