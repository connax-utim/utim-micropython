"""

The Worker dedicated to process "die" command arrived from Uhost.

The Worker simply calls the Utim's Die() method which terminates the Utim's execution.

"""

import logging
# from ..utilities.address import Address
from ..utilities.status import Status
from ..utilities.data_indexes import SubprocessorIndex

_SubprocessorIndex = SubprocessorIndex()

logger = logging.Logger('workers.utim_worker_die')


def process(utim, data):
    """
    Run process

    :param bytes data: data to process
    :param Queue outbound_queue: queue to write in
    """

    logger.debug("CommandWorkerDie process data: {}".format(
        [x for x in data[_SubprocessorIndex.body]]))

    utim.utim_die()

    res = data
    res[_SubprocessorIndex.status] = Status.STATUS_FINALIZED
    return res
