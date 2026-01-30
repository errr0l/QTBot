import json
from utils.common import load_characters_from_json
from db.db_helper import DBHelper
from entities.character import Character


def insert_character(character: Character):
    sql = """
        INSERT OR REPLACE INTO character
        (name, avatars, nicknames, arena_skill, awakening_passive, talent_tree, background, club,
        element, `year`, bonds, hobbies, type, extra, skins, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(sql, (
        character.name,
        json.dumps(character.avatars, ensure_ascii=False) if character.avatars else None,
        character.nicknames,
        json.dumps(character.arena_skill.__dict__, ensure_ascii=False),
        json.dumps(character.awakening_passive.__dict__, ensure_ascii=False) if character.awakening_passive else None,
        json.dumps(character.talent_tree.__dict__, ensure_ascii=False) if character.talent_tree else None,
        character.background,
        character.club,
        character.element,
        character.year,
        character.bonds,
        character.hobbies,
        character.type,
        json.dumps(character.extra, ensure_ascii=False) if character.extra else None,
        json.dumps(character.skins, ensure_ascii=False) if character.skins else None,
        json.dumps(character.tags, ensure_ascii=False) if character.tags else None
    ))


def insert_characters():
    for character in characters:
        insert_character(character)
    print(f"✅ 成功导入 {len(characters)} 个角色到数据库！")


if __name__ == "__main__":
    # todo python -m scripts.import_mock_data
    file_path = "data/main_character_v4_2.json"
    characters = load_characters_from_json(file_path)
    db_path = "data/wiki.db"
    db_helper = DBHelper(db_path=db_path)
    db_helper.init_db()
    with db_helper.get_connection() as conn:
        # conn.row_factory = sqlite3.Row
        # row = conn.execute(sql, (name,)).fetchone()
        # conn = db_helper.get_connection()
        insert_characters()
