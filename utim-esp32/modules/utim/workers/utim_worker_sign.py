"""
Encryption worker
"""

import logging
from ..utilities.cryptography import CryptoLayer
from ..utilities.address import Address
from ..utilities.status import Status
from ..utilities.data_indexes import SubprocessorIndex

_SubprocessorIndex = SubprocessorIndex()

logger = logging.Logger('workers.utim_worker_sign')


def process(utim, data):
    """
    Run process
    """

    res = None
    try:
        crypto = CryptoLayer(utim.get_session_key())
        logger.debug('Signing message with key {}'.format(utim.get_session_key()))
        res = crypto.sign(CryptoLayer.SIGN_MODE_SHA256, data[_SubprocessorIndex.body])
        logger.debug('Signed package: {}'.format(res))
    except TypeError:
        logger.error('Error appeared in signing message')
    except Exception as er:
        logger.debug(er)

    if res is None:
        return [Address.ADDRESS_UTIM, Address.ADDRESS_UHOST, Status.STATUS_FINALIZED, res]
    else:
        return [Address.ADDRESS_UTIM, Address.ADDRESS_UHOST, Status.STATUS_TO_SEND, res]
