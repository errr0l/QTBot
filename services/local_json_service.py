from typing import List

from services.storage_service import StorageService

from services.character_service import CharacterService
import json
from utils.common import convert_dict_attributes_to_json


class LocalJsonService(StorageService):
    """本地json服务"""

    def sync_data_from_list(self, characters: List[dict]):
        name_map = {}
        for char in characters:
            name_map[char['name']] = char

        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for char in data:
                if char['name'] in name_map:
                    char_in_name_map = name_map['name']
                    char.update(char_in_name_map)
                    if not name_map:
                        break
        if name_map:
            for val in name_map.values():
                data.append(val)

        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            return True

    def __init__(self, character_service: CharacterService, file_path: str):
        self.character_service = character_service
        self.file_path = file_path

    def sync_data_from_dict(self, character: dict):
        hit = False
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for char in data:
                if char['name'] == character['name']:
                    char.update(character)
                    hit = True
                    break
        if not hit:
            data.append(character)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            return True

    def sync_data_from_database(self, name: str):
        character = self.character_service.get_character_by_name(name=name)
        character = character.to_dict()
        return self.sync_data_from_dict(character)

    def sync_data(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            characters = json.load(f)
            convert_dict_attributes_to_json(characters)
        self.character_service.update_characters(characters=characters)
        return True

    # def push_characters(self, characters: List[dict]):
    #     # 1. 读取现有数据
    #     with open(self.file_path, 'r', encoding='utf-8') as f:
    #         data = json.load(f)
    #
    #     # 2. 添加新对象
    #     for char in characters:
    #         data.append(char)
    #
    #     # 3. 写回文件
    #     with open(self.file_path, 'w', encoding='utf-8') as f:
    #         json.dump(data, f, ensure_ascii=False, indent=2)
    #         return True
