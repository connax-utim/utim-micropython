"""
Encryption worker
"""

import logging
from ..utilities.cryptography import CryptoLayer
from ..utilities.address import Address
from ..utilities.status import Status
from ..utilities.data_indexes import SubprocessorIndex

_SubprocessorIndex = SubprocessorIndex()

logger = logging.Logger('workers.utim_worker_encrypt')


def process(utim, data):
    """
    Run process
    """

    res = None
    try:
        crypto = CryptoLayer(utim.get_session_key())
        logger.debug('Encrypting message with key {}'.format(utim.get_session_key()))
        res = crypto.encrypt(CryptoLayer.CRYPTO_MODE_AES, data[_SubprocessorIndex.body])
        logger.debug('Encrypted package: {}'.format(res))
    except ValueError:
        logger.error('Error appeared in encrypting message')
    if res is None:
        return [Address.ADDRESS_UTIM, Address.ADDRESS_UHOST, Status.STATUS_FINALIZED, res]
    else:
        return [Address.ADDRESS_UTIM, Address.ADDRESS_UHOST, Status.STATUS_PROCESS, res]
