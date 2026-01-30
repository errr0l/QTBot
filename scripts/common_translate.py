import sqlite3

from db.db_helper import DBHelper


def update_club():
    """更新部门英文名"""
    sql = """
        UPDATE character 
        SET club = CASE
            WHEN club = 'Art' THEN '艺术'
            WHEN club = 'Sports' THEN '运动'
            WHEN club = 'Science' THEN '科学'
            WHEN club = 'Destroyer' THEN '歼灭'
            WHEN club = 'All-rounder' THEN '全能'
            WHEN club = 'Literature' THEN '文学'
            -- 可继续添加更多映射
            ELSE club  -- 保持原值不变
        END
        WHERE club IN ('Art', 'Sports', 'Science', 'Destroyer', 'All-rounder', 'Literature');  -- 只更新需要改的行（可选但高效）
        """
    with db_helper.get_connection() as conn:
        conn.execute(sql)


def update_element():
    """更新元素"""
    sql = """
    update character
    set element = CASE
        when element = 'Water' then '水'
        when element = 'Fire' then '火'
        when element = 'Lightning' then '雷'
        when element = 'Wind' then '风'
        ELSE element  -- 保持原值不变
    end
    where element in ('Water', 'Fire', 'Lightning', 'Wind')
    """
    with db_helper.get_connection() as conn:
        conn.execute(sql)


def update_bonds():
    """更新羁绊，如果是英文，则选一个非英文别名"""
    from services.character_service import CharacterService
    from utils.name_mapper import NameMapper
    service = CharacterService(db_helper=db_helper)
    name_mapper = NameMapper(character_service=service)

    import re

    def is_english_name(_name: str) -> bool:
        """
        判断字符串是否为合理的英文名。
        支持：字母、空格、连字符、撇号。
        不支持：数字、中文、特殊符号、纯非字母字符串。
        """
        if not isinstance(_name, str) or not _name.strip():
            return False

        _name = _name.strip()
        # 正则：只允许字母、空格、-、'
        if not re.fullmatch(r"[A-Za-z\s\-']+", _name):
            return False

        # 必须至少有一个字母（排除 "   " 或 "---"）
        return any(c.isalpha() for c in _name)

    sql = """
    select name, bonds from character
    """
    with db_helper.get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql).fetchall()
        for row in rows:
            name = row['name']
            bonds = [item.strip() for item in row['bonds'].split(",")]
            updated_count = 0
            index = 0
            for bond in bonds:
                if is_english_name(bond):
                    aliases = name_mapper.get_all_aliases(bond)
                    if aliases:
                        for ali in aliases:
                            if ali and not is_english_name(ali):
                                bonds[index] = ali
                                updated_count += 1
                                break
                index += 1
            if updated_count > 0:
                conn.execute(
                    "update character set bonds = ? where name = ?",
                    (", ".join(bonds), name)
                )


def update1():
    sql = """
        select name, nicknames, bonds from character
        """
    with db_helper.get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql).fetchall()
        for row in rows:
            name = row['name']
            nicknames = [item.strip() for item in row['nicknames'].split(", ")]
            bonds = [item.strip() for item in row['bonds'].split(",")]
            conn.execute(
                "update character set nicknames = ?, bonds = ? where name = ?",
                ("、".join(nicknames), "、".join(bonds), name)
            )


if __name__ == "__main__":
    "通用翻译"
    db_path = "data/wiki.db"
    db_helper = DBHelper(db_path=db_path)
    db_helper.init_db()
    # update_bonds()
    update1()
    # update_club()
    # update_element()
