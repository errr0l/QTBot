from typing import List


class CharacterResponse:
    """6星及以上，才会返回觉醒被动；背景故事是单独的指令"""
    name: str
    nicknames: str
    avatar: str
    star: int
    arena_skill: 'CharacterResponse.Skill'
    club: str
    element: str
    year: str
    hobbies: str
    bonds: str
    type: int
    skins: List[dict] = None
    extra: dict = None
    tags: List[str] = None
    awakening_passive: 'CharacterResponse.Skill' = None
    talent_tree: 'CharacterResponse.Skill' = None
    background: str = None
    skin: dict = None

    def __getitem__(self, key):
        return getattr(self, key)

    class Skill:
        """被动技能冷却为0"""
        name: str
        lv: int
        desc: str
        cooldown: int

        def __init__(self, name, lv, desc, cooldown):
            self.name = name
            self.desc = desc
            self.lv = lv
            self.cooldown = cooldown
