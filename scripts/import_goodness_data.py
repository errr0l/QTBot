from db.db_helper import DBHelper
from services.character_service import CharacterService

if __name__ == "__main__":
    # todo python -m scripts.import_goodness_data
    db_path = "data/wiki.db"
    db_helper = DBHelper(db_path=db_path)
    service = CharacterService(db_helper=db_helper)
    service.import_characters_from_json("data_2026-01-25_18-52-44_type_2.json")
    print("ok")
