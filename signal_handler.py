from signal import SIGTERM, SIGINT, signal
import logging

class CatchSignal:
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        self.signal_issued = False

        signal(SIGTERM, self._handler)
        signal(SIGINT, self._handler)

    def _handler(self, signal, frame):
        self.logger.warning(f"Caught signal {signal}, terminating gracefully...")
        self.signal_issued = True