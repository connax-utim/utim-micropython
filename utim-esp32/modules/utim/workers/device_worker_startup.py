import logging
from ..utilities.tag import Tag
from ..utilities.address import Address
from ..utilities.status import Status
from ..utilities.data_indexes import SubprocessorIndex

_SubprocessorIndex = SubprocessorIndex()

logger = logging.Logger('workers.device_worker_startup')


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

    if (source == Address.ADDRESS_DEVICE and destination == Address.ADDRESS_UTIM and
            status == Status.STATUS_PROCESS):
        tag = body[0:1]

        if tag == Tag.INBOUND.NETWORK_READY:
            # Get SRP step
            srp_step = utim.get_srp_step()

            if srp_step is None:
                # Get SRP client
                srp_client = utim.get_srp_client()

                if srp_client is not None:
                    # Init SRP session
                    uname, a = srp_client.start_authentication()
                    command = Tag.UCOMMAND.assemble_hello(a)

                    # Set new SRP step value
                    utim.set_srp_step(1)

                    # Set output parameters
                    source = Address.ADDRESS_UTIM
                    destination = Address.ADDRESS_UHOST
                    status = Status.STATUS_PROCESS
                    body = command

                    logger.info('Starting SRP sequence...')

                    # Return STATUS_TO_SEND result
                    return [source, destination, status, body]

                else:
                    logger.error("SRP client is None")

            else:
                logger.error("Invalid SRP step: {}".format(str(srp_step)))

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
