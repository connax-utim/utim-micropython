"""
The Worker dedicated to process command "Try" arrived from Uhost.
The command means "Do calculate the SRP challenge"

The Worker checks if the SRP-client is still available, Worker parses the challenge extracting
two parameters, prepares them and tries to calculate the response by calling SRP-client's method
the corresponding SRP-client's method. In case the response was calculated successfully
the Worker builds the command "check" (meaning request to Uhost to validate the response),
packages it into TLV with the Tag "Data to be sent to Uhost" (Tag 0x2D)
and finally puts the message into the outbound queue.

in case the challenge response calculation failed the Worker builds the "error" command to Uhost
explaining the reason of failure, wraps it into TLV with Tag "Data to be sent to Uhost" (Tag 0x2D)
and puts it into the outbound queue.

"""

import logging
from ..utilities.tag import Tag
from ..utilities.address import Address
from ..utilities.status import Status
from ..utilities.data_indexes import SubprocessorIndex

_SubprocessorIndex = SubprocessorIndex()

logger = logging.Logger('workers.utim_worker_try')


def process(utim, data):
    """
    Run process

    :param Utim utim : utim
    :param bytes data: data to process
    """

    packet = None
    uhost_data = data[_SubprocessorIndex.body]

    tag1 = uhost_data[0:1]
    length_bytes1 = uhost_data[1:3]
    length1 = int.from_bytes(length_bytes1, 'big')
    value1 = uhost_data[3:3 + length1]

    tag2 = uhost_data[3 + length1:4 + length1]
    length_bytes2 = uhost_data[4 + length1: 6 + length1]
    length2 = int.from_bytes(length_bytes2, 'big')
    value2 = uhost_data[6 + length1:6 + length1 + length2]

    # Logging
    logger.debug('Tag1: {}'.format(str(tag1)))
    logger.debug('Length1: {}'.format(length1))
    logger.debug('Value1: {}'.format([x for x in value1]))
    logger.debug('Tag2: {}'.format(str(tag2)))
    logger.debug('Length2: {}'.format(length2))
    logger.debug('Value2: {}'.format([x for x in value2]))

    # Check real data length
    if (length1 == len(value1) and tag1 == Tag.UCOMMAND.TRY_FIRST and
            length2 == len(value2) and tag2 == Tag.UCOMMAND.TRY_SECOND):
        # Get SRP client
        srp_client = utim.get_srp_client()
        if srp_client is not None:
            # Calculate
            M = srp_client.process_challenge(value1, value2)
            logger.debug(str(M))
            logger.debug("M: {}".format(None if not isinstance(M, bytes) else [x for x in M]))

            # Answer
            if M is None:
                logger.debug('error try processing')
                packet = Tag.UCOMMAND.assemble_error('try processing'.encode('utf-8'))
            else:
                # Set new SRP step value
                utim.set_srp_step(2)

                packet = Tag.UCOMMAND.assemble_check(M)
        else:
            logger.debug('SRP client is None')
            return [data[0], data[1], Status.STATUS_FINALIZED, data[3]]

    else:
        logger.debug('error try wrong_parameters')
        command = Tag.UCOMMAND.assemble_error('try wrong_parameters'.encode('utf-8'))
        packet = Tag.OUTBOUND.assemble_for_network(command)

    # Put packet to the queue
    if packet is not None:
        logger.debug('put answer to outbound queue')
        return [Address.ADDRESS_UTIM, Address.ADDRESS_UHOST, Status.STATUS_PROCESS, packet]
