import logging
from ..utilities.tag import Tag
from ..utilities.address import Address
from ..utilities.status import Status
from ..utilities.data_indexes import SubprocessorIndex

_SubprocessorIndex = SubprocessorIndex()

logger = logging.Logger('workers.utim_worker_connection_string')


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
        cs_tag = body[0:1]
        cs_length_bytes = body[1:3]
        cs_length = int.from_bytes(cs_length_bytes, 'big')
        cs = body[3:3 + cs_length]

        if cs_tag == Tag.UCOMMAND.CONNECTION_STRING:
            # Parse platform tag
            pl_tag = cs[0:1]
            pl_length_bytes = cs[1:3]
            pl_length = int.from_bytes(pl_length_bytes, 'big')
            command = cs[3:3 + pl_length]

            if pl_tag in (Tag.UPLATFORM.PL_AZURE, Tag.UPLATFORM.PL_AWS):

                # Set output parameters
                source = Address.ADDRESS_UHOST
                destination = Address.ADDRESS_UTIM
                status = Status.STATUS_PROCESS
                body = command

                print('Connecting to cloud...')

                # Return STATUS_PROCESS result
                return [source, destination, status, body]

            else:
                logger.error("Invalid pl_tag: {}".format(str(pl_tag)))

        else:
            logger.error("Invalid cs_tag: {}".format(str(cs_tag)))

    else:
        logger.error("Invalid metadata: source={}, destination={}, status={}".format(
                     source,
                     destination,
                     status))

    # Return STATUS_FINALIZED result
    status = Status.STATUS_FINALIZED
    return [source, destination, status, body]
