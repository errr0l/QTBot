from abc import abstractmethod, ABC
from typing import List


class StorageService(ABC):
    @abstractmethod
    def sync_data(self):
        pass

    @abstractmethod
    def push_characters(self, characters: List[dict]):
        pass
