from abc import ABC, abstractmethod


class BasePreparator(ABC):

    @abstractmethod
    def prepare(self, text: str):
        ...
