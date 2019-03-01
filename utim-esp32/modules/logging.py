import sys

CRITICAL = 50
ERROR    = 40
WARNING  = 30
INFO     = 20
DEBUG    = 10
NOTSET   = 0

_level_dict = {
    CRITICAL: "CRIT",
    ERROR: "ERROR",
    WARNING: "WARN",
    INFO: "INFO",
    DEBUG: "DEBUG",
}

_stream = sys.stderr


class Logger:

    def __init__(self, name):
        self.level = NOTSET
        self.name = name

    def _level_str(self, level):
        if level in _level_dict:
            return _level_dict[level]
        return "LVL" + str(level)

    def log(self, level, msg, *args):
        string = "{:<8}{:-40}{}".format(self._level_str(level), str(self.name), str(msg))
        # if level >= _level:
        print(string)

    def debug(self, msg, *args):
        self.log(DEBUG, msg, *args)

    def info(self, msg, *args):
        self.log(INFO, msg, *args)

    def warning(self, msg, *args):
        self.log(WARNING, msg, *args)

    def error(self, msg, *args):
        self.log(ERROR, msg, *args)

    def critical(self, msg, *args):
        self.log(CRITICAL, msg, *args)


_level = ERROR
_loggers = {}


def getLogger(name):
    if name in _loggers:
        return _loggers[name]
    lgr = Logger(name)
    _loggers[name] = lgr
    return lgr


def info(msg, *args):
    getLogger(None).info(msg, *args)


def debug(msg, *args):
    getLogger(None).debug(msg, *args)


def basicConfig(level=INFO, filename=None, stream=None, format=None):
    global _level, _stream
    _level = level
    if stream:
        _stream = stream
    if filename is not None:
        print("logging.basicConfig: filename arg is not supported")
    if format is not None:
        print("logging.basicConfig: format arg is not supported")
