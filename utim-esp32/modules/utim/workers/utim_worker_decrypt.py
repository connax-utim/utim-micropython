"""
Encryption worker
"""

import logging
from ..utilities.cryptography import CryptoLayer
from ..utilities.address import Address
from ..utilities.status import Status
from ..utilities.data_indexes import SubprocessorIndex

_SubprocessorIndex = SubprocessorIndex()

logger = logging.Logger('workers.utim_worker_decrypt')


def process(utim, data):
    """
    Run process
    """

    res = None
    try:
        crypto = CryptoLayer(utim.get_session_key())
        logger.debug('Decrypting package {0} with key {1}'.format(data[_SubprocessorIndex.body],
                                                                  utim.get_session_key()))
        res = crypto.decrypt(data[_SubprocessorIndex.body])
        logger.debug('Decrypted message: {0}'.format(res))
    except ValueError:
        logger.error('Error appeared in decrypting message')
    if res is None:
        return [Address.ADDRESS_UHOST, Address.ADDRESS_UTIM, Status.STATUS_FINALIZED, res]
    else:
        return [Address.ADDRESS_UHOST, Address.ADDRESS_UTIM, Status.STATUS_PROCESS, res]
