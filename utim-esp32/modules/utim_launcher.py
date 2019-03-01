"""Simplest realization of Utim"""
import logging
import queue
from utim.connectivity.manager import ConnectivityConnectError
from utim.utim import Utim
from utim.connectivity.ttnd_manager import DataType
from utim.connectivity.manager import ConnectivityManager
from utim.utilities.tag import Tag
from utim.utilities.exceptions import UtimConnectionException, UtimInitializationError

logger = logging.Logger('launcher')

def main():
    """
    Main function
    """

    concrete_utim = None
    cm1 = None
    session_key = None

    logger.info("INIT rxQ")
    rx_queue = queue.Queue()
    logger.info("INIT txQ")
    tx_queue = queue.Queue()

    try:
        cm1 = ConnectivityManager(rx=tx_queue, tx=rx_queue)

        concrete_utim = Utim(rx=rx_queue, tx=tx_queue)
        concrete_utim.run()

        data1 = [DataType.DEVICE, Tag.INBOUND.NETWORK_READY]

        print("cm1 - send {0}".format(data1))
        cm1.send(data1)

        while True:
            data = cm1.receive()
            if data:
                print("RECEIVED DATA: {0}".format(data))
                session_key = data[1]
                # with open(expanduser("~")+'/.bashrc', 'a') as f:
                #     f.write('export UTIM_SESSION_KEY={}\n'.format(session_key))
                #     print(subprocess.check_output('./source_bashrc.sh'.split()))
                concrete_utim.stop()
                break

        print("RECEIVED SESSION KEY: {key}".format(key=session_key))

    except ConnectivityConnectError:
        logging.error("Connectivity error")
        print("Connectivity error")

    except UtimConnectionException as er:
        logging.error(er)

    except UtimInitializationError as er:
        logging.error(er)
        print('Invalid UTIM_MASTER_KEY')

    except (KeyboardInterrupt, EOFError):
        logging.info('Program interrupted')
        print('Program interrupted')

    finally:
        if concrete_utim:
            concrete_utim.stop()

        if cm1:
            cm1.stop()


if __name__ == '__main__':
    main()
