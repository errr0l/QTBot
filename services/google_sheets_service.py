from typing import List

import requests
from nonebot import logger

from services.character_service import CharacterService
from services.storage_service import StorageService


class GoogleSheetsService(StorageService):
    """谷歌表格服务"""

    def sync_data_from_dict(self, character: dict):
        pass

    def sync_data_from_list(self, characters: List[dict]):
        pass

    def sync_data_from_database(self, name: str):
        """还在犹豫，要不要实现这个。其实本地方式已经足够了"""
        pass

    def __init__(
            self,
            character_service: CharacterService,
            api_key: str,
            save_characters_endpoint: str,
            get_characters_endpoint: str):
        self.character_service = character_service
        self.api_key = api_key
        self.save_characters_endpoint = save_characters_endpoint
        self.get_characters_endpoint = get_characters_endpoint

    def sync_data(self):
        """同步数据"""
        logger.info("开始同步...")
        params = {
            "apiKey": self.api_key,
        }
        response = requests.get(self.get_characters_endpoint, params=params)
        logger.info(f"status_code: {response.status_code}")
        if response.status_code == 200:
            try:
                respData = response.json()
                if respData.get("code") == 200 or respData.get("message") == 'ok':
                    rows = respData.get("rows", [])
                    self.character_service.update_characters(characters=rows)
                    return True
            except Exception as error:
                logger.error(error)

    # def push_characters(self, characters: List[dict]):
    #     """
    #     推送角色数据到远程表格；
    #     首次使用apps scripts来初始化数据，也就是说，机器人内，无需批量操作
    #     """
    #     if not characters:
    #         return False
    #     logger.info(f"开始推送...")
    #     payload = {
    #         "apiKey": self.api_key,
    #         "data": characters
    #     }
    #     response = requests.post(self.save_characters_endpoint, json=payload)
    #     logger.info(f"status_code: {response.status_code}")
    #     logger.info(response.text)
    #     if response.status_code == 200:
    #         try:
    #             respData = response.json()
    #             if respData.get("code") == 200:
    #                 return True
    #         except Exception as error:
    #             logger.error(error)
