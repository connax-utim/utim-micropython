"""
Python3 queue.Queue realisation with Micropython ucollections.deque

"""

from collections import deque

__all__ = ['Empty', 'Full', 'Queue']


class Empty(Exception):
    'Exception raised by get_nowait().'
    pass


class Full(Exception):
    'Exception raised by put_nowait().'
    pass


class Queue(object):
    def __init__(self):
        self.q = deque((), 128)

    def put_nowait(self, data):
        if(self.full()):
            raise Full
        self.q.append(data)

    def get_nowait(self):
        if(self.empty()):
            raise Empty
        return self.q.popleft()

    def empty(self):
        return (len(self.q) == 0)

    def full(self):
        return (len(self.q) > 128)
