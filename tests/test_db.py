import configparser
import sqlite3

from bo.wiki_instructions import WikiInstructions
from db.db_helper import DBHelper
from services.character_service import build_character_from_row, CharacterService
from services.qt_wiki_crawler import QTWikiCrawler

# from nonebot.adapters.console import MessageSegment

from services.translation_service import TranslationService
from utils.common import build_character_response

if __name__ == '__main__':
    db_path = "data/wiki.db"
    db_helper = DBHelper(db_path=db_path)
    # service = CharacterService(db_helper=db_helper)
    # config = configparser.ConfigParser()
    # config.read('config.ini', encoding='utf-8')
    # crawler = QTWikiCrawler(list_page_paths=["/wiki/Goddess_List"], character_service=service)
    # character = crawler.scrape_character("Iset")
    # print(character)
    # char = service.get_character_by_name("Alina")
    # if char:
    #     wiki_ins = WikiInstructions()
    #     wiki_ins.name = "Alina"
    #     character_response = build_character_response(wiki_instructions=wiki_ins, character=char)
    #     trans_service = TranslationService(
    #         appid=config['baidu_fanyi'].get("appid"),
    #         app_key=config['baidu_fanyi'].get("app_key"),
    #         endpoint=config['baidu_fanyi'].get("endpoint"),
    #     )
    #     result = trans_service.translate_character(character_response)
    #     print("--r--")
    #     print(result)
    # service.import_characters_from_json("data_2026-01-25_18-43-04_type_2.json")
    # print("ok")
