from abc import abstractmethod, ABC
from typing import List


class StorageService(ABC):
    @abstractmethod
    def sync_data(self):
        """外部存储同步至数据库"""
        pass

    @abstractmethod
    def sync_data_from_database(self, name: str):
        """同步指定角色数据到外部存储"""
        pass

    @abstractmethod
    def sync_data_from_list(self, characters: List[dict]):
        """将传入的角色数据列表同步至外部存储"""
        pass

    @abstractmethod
    def sync_data_from_dict(self, character: dict):
        pass
