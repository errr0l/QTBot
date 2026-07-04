from typing import cast

from containers.app_container import AppContainer
from services.character_service import CharacterService
from services.local_json_service import LocalJsonService
from services.qt_wiki_crawler import QTWikiCrawler, parse_character_page, parse_goodness_page

if __name__ == "__main__":
    # todo python -m scripts.crawl_latest
    container = AppContainer()
    container.config.from_ini("config.ini")
    qt_wiki_crawler = cast(QTWikiCrawler, container.qt_wiki_crawler())
    storage_service = cast(LocalJsonService, container.storage_service())
    character_service = cast(CharacterService, container.character_service())
    entry = {
        "name": "Durga",
        "url": "",
        "avatar": "",
        "awakened_avatar": ""
    }
    characters = []
    with open(f"/Users/errol/personalplace/QTBot/{entry.get('name')}.html", "r", encoding="utf-8") as _f:
        html = _f.read()
        entry['html'] = html
        char = parse_goodness_page(entry=entry)
        print(char)
        characters.append(char)
    # char = qt_wiki_crawler.scrape_latest_character()
    character_service.save_characters(characters)
    storage_service.sync_data_from_database(name=entry.get("name"))
