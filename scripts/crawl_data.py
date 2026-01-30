from db.db_helper import DBHelper
from services.qt_wiki_crawler import QTWikiCrawler
from services.character_service import CharacterService

if __name__ == "__main__":
    # todo python -m scripts.crawl_data
    list_page_paths = [
        "/wiki/Character_List",
        "/wiki/Goddess_List"
    ]
    db_path = "data/wiki.db"
    db_helper = DBHelper(db_path=db_path)
    service = CharacterService(db_helper=db_helper)
    crawler = QTWikiCrawler(list_page_paths=list_page_paths, character_service=service)
    crawler.run()
