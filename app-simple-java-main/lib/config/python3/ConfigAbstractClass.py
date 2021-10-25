from abc import ABC, abstractmethod
import os

# --------------------------------
# -- Class: ConfigAbstractClass --
# --------------------------------
class ConfigAbstractClass(ABC):

    def __init__(self, args: object):
        self.args = args
        super().__init__()

    @abstractmethod
    def query(self, path) -> object:
        pass

    @abstractmethod
    def query_with_default(self, path, default_value) -> object:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass
