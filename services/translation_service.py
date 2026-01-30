import requests
import random
from hashlib import md5

from vo.character_response import CharacterResponse


def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()


class TranslationService:
    """翻译服务（百度）"""

    def __init__(self, appid: str, app_key: str, endpoint: str):
        self.appid = appid
        self.app_key = app_key
        self.url = endpoint

    def translate(self, query: str, original: str = 'en', to: str = 'zh'):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        salt = random.randint(32768, 65536)
        sign = make_md5(self.appid + query + str(salt) + self.app_key)
        payload = {
            'appid': self.appid,
            'q': query,
            'from': original,
            'to': to,
            'salt': salt,
            'sign': sign
        }
        r = requests.post(self.url, params=payload, headers=headers)
        result = r.json()
        if result:
            # print(json.dumps(result, indent=4, ensure_ascii=False))
            if 'trans_result' in result:
                return result['trans_result']

    def translate_goodness(self, character_response: CharacterResponse):
        """翻译女神"""
        lines = [
            character_response.name,
            character_response.club,
            character_response.arena_skill.name,
            character_response.arena_skill.desc.replace("\n", ""),
        ]
        if character_response.background:
            lines.append(character_response.background.replace("\n", ""))
        if character_response.hobbies:
            lines.append(character_response.hobbies)
        if character_response.skin:
            lines.append(character_response.skin.get("name"))
            lines.append(character_response.skin.get("desc"))
        result = self.translate("\n".join(lines))
        character_response.name = result[0].get("dst")
        character_response.club = result[1].get("dst")
        character_response.arena_skill.name = result[2].get("dst")
        character_response.arena_skill.desc = result[3].get("dst")
        index = 3
        if character_response.background:
            index += 1
            character_response.background = result[index].get("dst")
        if character_response.hobbies:
            index += 1
            character_response.hobbies = result[index].get("dst")
        if character_response.skin:
            index += 1
            character_response.skin['name'] = result[index].get("dst")
            index += 1
            character_response.skin['desc'] = result[index].get("dst")

    def translate_character(self, character_response: CharacterResponse):
        """翻译角色"""
        if character_response.type == 2:
            return self.translate_goodness(character_response)
        lines = [
            character_response.name,
            character_response.club,
            character_response.arena_skill.name,
            character_response.arena_skill.desc.replace("\n", ""),
            character_response.element
        ]
        if character_response.awakening_passive:
            lines.append(character_response.awakening_passive.name)
            lines.append(character_response.awakening_passive.desc.replace("\n", ""))
        if character_response.talent_tree:
            lines.append(character_response.talent_tree.name)
            lines.append(character_response.talent_tree.desc.replace("\n", ""))
        if character_response.background:
            lines.append(character_response.background.replace("\n", ""))
        if character_response.hobbies:
            lines.append(character_response.hobbies)
        if character_response.skin:
            lines.append(character_response.skin.get("name"))
        result = self.translate("\n".join(lines))
        character_response.name = result[0].get("dst")
        character_response.club = result[1].get("dst")
        character_response.arena_skill.name = result[2].get("dst")
        character_response.arena_skill.desc = result[3].get("dst")
        character_response.element = result[4].get("dst")
        index = 4
        if character_response.awakening_passive:
            index += 1
            character_response.awakening_passive.name = result[index].get("dst")
            index += 1
            character_response.awakening_passive.desc = result[index].get("dst")
        if character_response.talent_tree:
            index += 1
            character_response.talent_tree.name = result[index].get("dst")
            index += 1
            character_response.talent_tree.desc = result[index].get("dst")
        if character_response.background:
            index += 1
            character_response.background = result[index].get("dst")
        if character_response.hobbies:
            index += 1
            character_response.hobbies = result[index].get("dst")
        if character_response.skin:
            index += 1
            character_response.hobbies = result[index].get("dst")
