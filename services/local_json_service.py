from typing import List
from services.storage_service import StorageService

from services.character_service import CharacterService
import json
from utils.common import convert_dict_attributes_to_json


class LocalJsonService(StorageService):
    """本地json服务"""

    def __init__(self, character_service: CharacterService, file_path: str):
        self.character_service = character_service
        self.file_path = file_path

    def sync_data(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            characters = json.load(f)
            convert_dict_attributes_to_json(characters)
        self.character_service.update_characters(characters=characters)
        return True

    def push_characters(self, characters: List[dict]):
        # 1. 读取现有数据
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 2. 添加新对象
        for char in characters:
            data.append(char)

        # 3. 写回文件
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            return True
