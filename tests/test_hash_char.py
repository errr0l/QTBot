import json

from db.db_helper import DBHelper
from services.character_service import CharacterService
from utils.common import convert_dict_attributes_to_json, hash_character

if __name__ == "__main__":
    # todo python -m tests.test_hash_char

    db_path = "data/wiki.db"
    db_helper = DBHelper(db_path=db_path)
    character_service = CharacterService(db_helper=db_helper)
    characters_in_db = character_service.get_all_characters()

    with open("data/characters.json", 'r', encoding='utf-8') as f:
        characters = json.load(f)
        convert_dict_attributes_to_json(characters)
    pending = []
    # print(characters_in_db[0])

    char1 = characters[0]
    # print(char1)
    print(hash_character(char1))
    print('------')
    print(hash_character(characters_in_db[0]))
