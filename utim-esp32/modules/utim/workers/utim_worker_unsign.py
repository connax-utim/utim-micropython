"""
Encryption worker
"""

import logging
from ..utilities.cryptography import CryptoLayer
from ..utilities.address import Address
from ..utilities.status import Status
from ..utilities.data_indexes import SubprocessorIndex

_SubprocessorIndex = SubprocessorIndex()

logger = logging.Logger('workers.utim_worker_unsign')


def process(utim, data):
    """
    Run process
    """

    res = None
    try:
        crypto = CryptoLayer(utim.get_session_key())
        logger.debug('Unsigning package {0} with key {1}'
                     .format(data[_SubprocessorIndex.body], utim.get_session_key()))
        res = crypto.unsign(data[_SubprocessorIndex.body])
        logger.debug('Unsigned message: {0}'.format(res))
    except TypeError:
        logger.error('Error appeared in unsigning message')
    if res is None:
        return [Address.ADDRESS_UHOST, Address.ADDRESS_UTIM, Status.STATUS_FINALIZED, res]
    else:
        return [Address.ADDRESS_UHOST, Address.ADDRESS_UTIM, Status.STATUS_PROCESS, res]
