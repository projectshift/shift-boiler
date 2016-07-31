from blinker import Namespace as BlinkerNamespace
from contextlib import contextmanager


class Namespace(BlinkerNamespace):
    """
    Namespace
    An extension to blinker namespace that provides a context manager for
    testing, which allows to temporarily disconnect all receivers.
    """
    @contextmanager
    def disconnect_receivers(self):
        receivers = {}
        try:
            for name in self:
                event = self[name]
                receivers[name] = event.receivers
                event.receivers = {}
            yield {}

        finally:
            for name in self:
                event = self[name]
                event.receivers = receivers[name]


