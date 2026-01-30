# import sqlite3
#
# from utils.message_helper import build_markdown_content
# from db.db_helper import DBHelper
# from services.character_service import build_character_from_row
# from utils.common import build_character_response
#
# if __name__ == '__main__':
#     db_path = "data/wiki.db"
#     db_helper = DBHelper(db_path=db_path)
#     sql = """
#         SELECT name, avatars, nicknames, arena_skill, awakening_passive, talent_tree, bonds,
#         background, club, element, year, hobbies FROM `character` WHERE name = ?
#         """
#     with db_helper.get_connection() as conn:
#         conn.row_factory = sqlite3.Row
#         row = conn.execute(sql, ("Kirsten",)).fetchone()
#         if row:
#             r = build_character_from_row(row)
#             character_response = build_character_response(None, r)
#             print(character_response.arena_skill.desc)
#             markdown_content = build_markdown_content(character_response=character_response)
#             print(markdown_content)
