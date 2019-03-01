class ProcessorIndex:
    """
    Processor indexes
    """
    def __init__(self):
        self.address = 0
        self.body = 1


class SubprocessorIndex:
    """
    Subprocessor indexes
    """
    def __init__(self):
        self.source = 0
        self.destination = 1
        self.status = 2
        self.body = 3
