"""Utim exceptions module"""


class UtimException(Exception):
    """
    Utim Base Exception
    """
    pass


class UtimConnectionException(UtimException):
    """
    Connection Exception class

    The exception is raised when:
     * AMQP configuration has wrong parameters (config.py)
    """
    pass


class UtimExchangeException(UtimException):
    """
    Exchange Exception class

    The exception is raised when:
     * destination in send function is not string or zero length string
    """
    pass


class UtimUnknownException(UtimException):
    """
    Unknown Exception class

    The exception is raised when raised any Exception except
    * pika.exceptions.ConnectionClosed
    * pika.exceptions.ProbableAuthenticationError
    * pika.exceptions.ChannelClosed
    """
    pass


class UtimInitializationError(UtimException):
    """
    Utim Initialization Error

    The exception is raised when:
    * Utim was started without serial number
    """


class UtimUncallableCallbackError(UtimException):
    """
    Utim uncallable callback error

    The exception is raised when:
     * Uncallable object was given to method as callback
    """
    pass

"""
Connectivity Manager Exceptions
"""

class ManagerException(Exception):
    """
    General Top Manager exception
    """

    pass


class ManagerMethodException(ManagerException):
    """
    Required method of object does not exist exception
    """

    pass


class ManagerDataTypeException(ManagerException):
    """
    Unknown data type exception
    """

    pass

"""
Utim Device layer exceptions
"""
class UtimDeviceException(Exception):
    """
    Utim device exception
    """

    pass


class UtimDeviceExceptionInvalidMethods(UtimDeviceException):
    """
    Invalid method exception
    """

    pass


class UtimDeviceInvalidDataException(UtimDeviceException):
    """
    Invalid data exception
    """

    pass

"""
DataLink layer exceptions
"""


class DataLinkManagerException(Exception):
    """
    Base DataLinkManagerException
    """
    pass


class DataLinkManagerWrongTypeException(DataLinkManagerException):
    """
    DataLink Wrong Type exception
    """
    pass


class DataLinkManagerWrongArgsException(DataLinkManagerException):
    """
    DataLink Manager Wrong arguments Exception
    """
    pass


class DataLinkManagerInitializationException(DataLinkManagerException):
    """
    DataLink Initialization Exception
    """
    pass


class DataLinkRealisationException(Exception):
    """
    Base DataLink Layer Realisation Exception
    Крч если будут Queue и Uart кидать исключения, наследовать отсюда
    """
    pass


class DataLinkRealisationConnectionException(DataLinkRealisationException):
    """
    DataLink Realisation Connection Exception
    """
    pass


class DataLinkRealisationWrongArgsException(DataLinkRealisationException):
    """
    DataLink Realisation Wrong arguments Exception
    """
    pass
