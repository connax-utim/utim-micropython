import logging
from ..utilities.tag import Tag
from ..utilities.address import Address
from ..utilities.status import Status
from ..utilities.data_indexes import SubprocessorIndex

_SubprocessorIndex = SubprocessorIndex()

logger = logging.Logger('workers.utim_worker_platform_verify')


def process(utim, data):
    """
    Run process

    :param Utim utim: Utim instance
    :param list data: Data to process [source, destination, status, body]
    :return list: [from, to, status, body]
    """

    source = data[_SubprocessorIndex.source]
    destination = data[_SubprocessorIndex.destination]
    status = data[_SubprocessorIndex.status]
    body = data[_SubprocessorIndex.body]

    if (source == Address.ADDRESS_UHOST and destination == Address.ADDRESS_UTIM and
            status == Status.STATUS_PROCESS):
        tag = body[0:1]
        length_bytes = body[1:3]
        length = int.from_bytes(length_bytes, 'big')
        command = body[3:3 + length]

        if tag == Tag.UCOMMAND.TEST_PLATFORM_DATA:
            # Set output parameters
            source = Address.ADDRESS_UTIM
            destination = Address.ADDRESS_PLATFORM
            status = Status.STATUS_TO_SEND
            body = [command, {}, 'verify', True]

            # Return STATUS_TO_SEND result
            logger.debug("Send test data via platform: {}".format(str(body)))
            return [source, destination, status, body]

        else:
            logger.error("Invalid tag: {}".format(str(tag)))

    else:
        logger.error("Invalid metadata: source={}, destination={}, status={}".format(
                     source,
                     destination,
                     status))

    # Return STATUS_FINALIZED result
    status = Status.STATUS_FINALIZED
    return [source, destination, status, body]
