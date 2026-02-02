from dataclasses import dataclass, asdict
from typing import List, Union


@dataclass
class Character:
    """
    角色实体对象；是以wiki页面构建的实体对象，需要根据星级来决定展示内容，所以，该实体对象不是用来直接返回的；
    目前把技能、天赋、觉醒被动都抽象为<角色技能>
    """
    name: str
    nicknames: str  # 花名
    background: str
    club: str
    element: str
    year: str
    bonds: str
    hobbies: str
    type: int  # 角色类型；1=通常，2=女神
    arena_skill: Union['Character.CharacterSkill', dict]  # 竞技场技能（静态）（默认显示五星）
    awakening_passive: Union['Character.CharacterPassiveSkill', dict] = None  # 觉醒被动
    talent_tree: Union['Character.CharacterPassiveSkill', dict] = None  # 天赋树
    extra: dict = None
    avatars: List[str] = None  # 随机返回
    skins: List[dict] = None
    tags: List[str] = None
    id: int = None
    story_skill: dict = None
    created_at: str = None
    last_updated: str = None
    translated: int = None

    def __getitem__(self, key):
        return getattr(self, key)

    @dataclass
    class CharacterSkill:
        """主动；使用星级来读取具体技能描述"""
        name: str
        icon: str
        cooldown: int
        descriptions: List[str]

        def to_dict(self):
            return asdict(self)

    @dataclass
    class CharacterPassiveSkill:
        """被动；被动有个'指令'字段，可附加一些额外的功能，比方说，被动减主动技冷却，由人工添加"""
        name: str
        icon: str
        descriptions: List[str]
        instructions: List[dict] = None
        extra: str = None

        def to_dict(self):
            return asdict(self)

    def to_dict(self):
        d = asdict(self)
        arena_skill = d['arena_skill']
        # arena_skill有可能是dict
        if arena_skill and isinstance(arena_skill, Character.CharacterSkill):
            d['arena_skill'] = arena_skill.to_dict()
        awakening_passive = d['awakening_passive']
        if awakening_passive and isinstance(arena_skill, Character.CharacterPassiveSkill):
            d['awakening_passive'] = awakening_passive.to_dict()
        arena_skill = d['arena_skill']
        if arena_skill and isinstance(arena_skill, Character.CharacterPassiveSkill):
            d['arena_skill'] = arena_skill.to_dict()

        return d
