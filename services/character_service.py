import json
import sqlite3
from typing import Optional, List, Union
from entities.character import Character
from dependency_injector.wiring import inject, Provide
from typing import cast
from db.db_helper import DBHelper
from utils.common import load_characters_from_json
from nonebot import logger


def build_dict_from_row(row):
    return {
        "id": row['id'],
        "name": row['name'],
        "avatars": row['avatars'],
        "nicknames": row['nicknames'],
        "arena_skill": row['arena_skill'],
        "awakening_passive": row['awakening_passive'],
        "talent_tree": row['talent_tree'],
        "background": row['background'],
        "club": row['club'],
        "element": row['element'],
        "year": row['year'],
        "hobbies": row['hobbies'],
        "bonds": row['bonds'],
        "type": row['type'],
        "extra": row['extra'],
        "skins": row['skins'],
        "tags": row['tags'],
        "created_at": row['created_at'],
        "last_updated": row['last_updated'],
        "translated": row['translated']
    }


def build_character_from_row(row):
    d = build_dict_from_row(row)
    arena_skill = json.loads(d.pop("arena_skill"))
    awakening_passive = d.pop("awakening_passive")
    talent_tree = d.pop("talent_tree")
    extra = d.pop('extra')
    skins = d.pop('skins')
    tags = d.pop("tags")
    return Character(
        **d,
        arena_skill=Character.CharacterSkill(**arena_skill),
        awakening_passive=Character.CharacterPassiveSkill(**json.loads(awakening_passive)) if awakening_passive else None,
        talent_tree=Character.CharacterPassiveSkill(**json.loads(talent_tree)) if talent_tree else None,
        extra=json.loads(extra) if extra else None,
        skins=json.loads(skins) if skins else None,
        tags=json.loads(tags) if tags else None,
    )


@inject
class CharacterService:
    def __init__(self, db_helper=cast(DBHelper, Provide['db_helper'])):
        self.db_helper = db_helper

    def import_characters_from_json(self, path: str):
        """如果有重复的话，会忽略"""
        characters = load_characters_from_json(path)
        for char in characters:
            self.save_character(char)

    def save_characters(self, characters: List[Character]):
        for char in characters:
            self.save_character(char)

    def save_character(self, character: Character):
        sql = """
        INSERT OR IGNORE INTO character
        (name, avatars, nicknames, arena_skill, awakening_passive, talent_tree, background, club,
        element, `year`, bonds, hobbies, type, extra, skins, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.db_helper.get_connection() as conn:
            conn.execute(sql, (
                character.name,
                json.dumps(character.avatars, ensure_ascii=False) if character.avatars else None,
                character.nicknames,
                json.dumps(character.arena_skill.__dict__, ensure_ascii=False),
                json.dumps(character.awakening_passive.__dict__,
                           ensure_ascii=False) if character.awakening_passive else None,
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

    def update_characters(self, characters: List[dict]):
        """批量更新角色"""
        if not characters:
            return None
        with self.db_helper.get_connection() as conn:
            sql = """
            update character set
            avatars = :avatars, nicknames = :nicknames, arena_skill = :arena_skill,
            awakening_passive = :awakening_passive, talent_tree = :talent_tree, background = :background,
            club = :club, element = :element, year = :year, bonds = :bonds, hobbies = :hobbies,
            type = :type, extra = :extra, skins = :skins, tags = :tags, translated = :translated,
            created_at = :created_at, last_updated = :last_updated
            where name = :name
            """
            conn.executemany(sql, characters)
            logger.info(f"受影响行数：{conn.rowcount}")
            return True

    def get_character_by_name(self, name: str, data_type: int = 1) -> Union[Character, dict, None]:
        """
        按标准名称查询；
        这里的角色，应该包含角色基础信息、角色技能，后续可能会加入皮肤、背景故事、活动等等
        """
        sql = """
        SELECT id, name, avatars, nicknames, arena_skill, awakening_passive, talent_tree, bonds,
        background, club, element, year, hobbies, type, extra, skins, tags, created_at, last_updated, translated FROM character WHERE name = ?
        """
        with self.db_helper.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(sql, (name,)).fetchone()
            if not row:
                return None
            if data_type == 1:
                return build_character_from_row(row)
            else:
                return build_dict_from_row(row)

    def build_character_map(self) -> Optional[dict]:
        """构建角色map"""
        sql = "SELECT name FROM character"
        result = {}
        with self.db_helper.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql).fetchall()
            for row in rows:
                result[row['name']] = True
        return result

    def build_character_alias(self) -> Optional[List[dict]]:
        """构建别名mapper"""
        sql = "SELECT name, nicknames FROM character"
        result = []
        with self.db_helper.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql).fetchall()
            for row in rows:
                character_aliases = {
                    "name": row['name'],
                    "aliases":
                        [part.strip() for part in row['nicknames'].split(",")]
                        if row['nicknames'] is not None else []
                }
                result.append(character_aliases)
        return result
