"""
The command worker
"""

import logging
# from ..utilities.tag import Tag
from ..utilities.address import Address
from ..utilities.status import Status
from ..utilities.data_indexes import SubprocessorIndex

_SubprocessorIndex = SubprocessorIndex()

logger = logging.Logger('workers.utim_worker_authentic')


def process(utim, data):
    """
    Run  process
    """

    logger.debug("UTIM is authentic now!")
    res = data
    res[_SubprocessorIndex.status] = Status.STATUS_FINALIZED

    logger.debug(data)
    packet = [Address.ADDRESS_UTIM,
              Address.ADDRESS_DEVICE,
              Status.STATUS_TO_SEND,
              utim.get_session_key()]

    # Put packet to the queue
    if packet is not None:
        logger.debug('put answer to device queue')
        return packet
    return res
