from abc import ABCMeta, abstractmethod
from typing import TypeVar

T = TypeVar("T")


class FilterInterface(metaclass=ABCMeta):
    @abstractmethod
    def process(self, input: T) -> T:
        raise NotImplementedError("use derived class instead")