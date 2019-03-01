import logging
import uos as os
from ..utilities.tag import Tag
from ..utilities.address import Address
from ..utilities.status import Status
from ..utilities.data_indexes import SubprocessorIndex

_SubprocessorIndex = SubprocessorIndex()

logger = logging.Logger('workers.utim_worker_init')


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
        value = body[3:3 + length]

        if tag == Tag.UCOMMAND.INIT:
            # Get SRP step
            srp_step = utim.get_srp_step()

            if srp_step == 2:
                # Get SRP client
                srp_client = utim.get_srp_client()

                if srp_client is not None:
                    # Get Key
                    srp_client.verify_session(value)
                    utim.set_session_key(srp_client.get_session_key())

                    # Answer
                    session_key = utim.get_session_key()
                    logger.debug("+++++++++++session key++", session_key)
                    if session_key is not None:
                        logger.debug('Today I\'m starting new life with new name! And key')
                        rand_data = os.urandom(32)
                        logger.debug('Random data: {} and session_key: {}'.format(
                                     str(rand_data),
                                     str(session_key)))
                        command = Tag.UCOMMAND.assemble_trusted(rand_data)
                        print('SRP completed')
                    else:
                        logger.debug('error init processing')
                        command = Tag.UCOMMAND.assemble_error('init processing'.encode('utf-8'))

                    # Set output parameters
                    source = Address.ADDRESS_UTIM
                    destination = Address.ADDRESS_UHOST
                    status = Status.STATUS_PROCESS
                    body = command

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
