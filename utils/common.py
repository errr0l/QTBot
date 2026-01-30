import random
import re
import json
from typing import List

from bo.wiki_scrape_instructions import SuperInstructions
from entities.character import Character
from bo.wiki_instructions import WikiInstructions
from nonebot import logger

from vo.character_response import CharacterResponse


def convert_json_to_characters(data: List[dict]):
    characters = []
    if not data:
        return characters
    for item in data:
        talent_tree = None
        arena_skill = None
        awakening_passive = None
        extra = None
        skins = None
        avatars = None
        if "talent_tree" in item:
            talent_tree_data = item.pop("talent_tree")
            if talent_tree_data:
                talent_tree = Character.CharacterPassiveSkill(
                    **(talent_tree_data if isinstance(talent_tree_data, dict) else json.loads(talent_tree_data))
                )
        if "arena_skill" in item:
            arena_skill_data = item.pop("arena_skill")
            if arena_skill_data:
                arena_skill = Character.CharacterSkill(
                    **(arena_skill_data if isinstance(arena_skill_data, dict) else json.loads(arena_skill_data))
                )
        if "awakening_passive" in item:
            awakening_passive_data = item.pop("awakening_passive")
            if awakening_passive_data:
                awakening_passive = Character.CharacterPassiveSkill(
                    **(awakening_passive_data if isinstance(awakening_passive_data, dict) else json.loads(
                        awakening_passive_data))
                )
        if "extra" in item:
            if extra := item.pop("extra"):
                extra = extra if isinstance(extra, dict) else json.loads(extra)
        if "skins" in item:
            if skins := item.pop("skins"):
                skins = skins if isinstance(skins, list) else json.loads(skins)
        if "avatars" in item:
            if avatars := item.pop("avatars"):
                avatars = avatars if isinstance(avatars, list) else json.loads(avatars)
        # 创建 Character 实例
        char = Character(
            talent_tree=talent_tree,
            arena_skill=arena_skill,
            extra=extra, skins=skins, avatars=avatars,
            awakening_passive=awakening_passive, **item)
        characters.append(char)
    return characters


def load_characters_from_json(file_path: str) -> List[Character]:
    """从 JSON 文件加载角色列表"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return convert_json_to_characters(data)


def get_instruction_number(_input: str, _max: int, chinese_to_digit: dict):
    if not _input:
        num = _max
    elif _input in chinese_to_digit:
        num = chinese_to_digit[_input]
    else:
        num = int(_input)
    return num if 0 < num <= _max else _max


def parse_super_instructions(_input: str):
    """
    如果第二个参数不是"女神"、"角色"的话，就认为是[角色名称]
    1、抓取-女神-10条数据，抓取-角色-10条数据
    2、抓取-[角色]
    3、抓取-10条数据
    """
    instructions = [part.strip() for part in _input.split("-")]
    instructions = instructions[1:]
    super_instructions = SuperInstructions()
    pattern = r'(\d+)条'
    if len(instructions) > 1:
        if instructions[0] == "女神":
            super_instructions.type = 2
        if instructions[0] == "角色":
            super_instructions.type = 1

        if match := re.search(pattern, instructions[1]):
            count = int(match.group(1))
            super_instructions.count = count
            return super_instructions
        else:
            # 表示失败指令
            super_instructions.type = -1
    if len(instructions) == 1:
        if match := re.search(pattern, instructions[0]):
            count = int(match.group(1))
            super_instructions.count = count
            return super_instructions
        # 否则当做名称
        super_instructions.char_name = instructions[0]
    return super_instructions


def parse_instructions(_input: str) -> WikiInstructions:
    """
    解析指令；
    以角色名称开头，可包含其他指令,多个指令以"-"相隔，如：阿丽娜，阿丽娜-7星-天赋10，阿丽娜-背景故事
    """
    instructions = [part.strip() for part in _input.split("-")]
    wiki_instructions = WikiInstructions()
    name = instructions[0].split(":")
    wiki_instructions.name = name[0]
    if len(name) > 1 and name[1].lower() == 'tl':
        wiki_instructions.tl = True

    # 没有其他指令时，直接返回
    if len(instructions) == 1:
        return wiki_instructions
    pattern = r'(?:[1-8]|一|二|三|四|五|六|七|八)星'
    chinese_to_digit = {
        "一": 1,
        "二": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
        "十": 10
    }

    # 如果不指定，则返回技能、天赋、被动，如果指定的话，只返回指定项
    # 比方说[/查询 水狐] -> 返回技能、天赋、被动，[/查询 水狐-7星] -> 返回技能、被动，[/查询 水狐-天赋8] -> 返回天赋
    # [/查询 水狐-8星-天赋10]，同等于[/查询 水狐]
    # [/查询 水狐-皮肤1]，返回皮肤1「头像改为皮肤头像，随机返回一个」，并附加满级皮肤数据「其他不重要，算了录进去也行」
    # 截取前三个指令（太长了，不美观）
    wiki_instructions.star = 0
    wiki_instructions.talent_lv = 0
    for item in instructions[1:4]:
        if not wiki_instructions.star:
            # 包含主动和被动
            if item.startswith("技能"):
                star = item[2:].strip()
                wiki_instructions.star = get_instruction_number(
                    _input=star, _max=8, chinese_to_digit=chinese_to_digit)
                continue
            if bool(re.match(pattern, item)):
                star = item[0].strip()
                wiki_instructions.star = get_instruction_number(
                    _input=star, _max=8, chinese_to_digit=chinese_to_digit)
                continue
        if not wiki_instructions.talent_lv:
            if item.startswith("天赋"):
                talent_lv = item[2:].strip()
                wiki_instructions.talent_lv = get_instruction_number(
                    _input=talent_lv, _max=10, chinese_to_digit=chinese_to_digit)
                continue
        if not wiki_instructions.background:
            if item.startswith("背景"):
                wiki_instructions.background = True
                continue
        if wiki_instructions.skin_order == 0 and item.startswith("皮肤"):
            skin_params = item[2:].strip()
            if skin_params:
                skin_params = skin_params.split(":")
                skin_order = skin_params[0]
                skin_order = int(skin_order) if skin_order else 1
                wiki_instructions.skin_order = skin_order
                wiki_instructions.skin_lv = int(skin_params[1]) if len(skin_params) == 2 else 10
            else:
                wiki_instructions.skin_order = 1
                wiki_instructions.skin_lv = 10
    logger.info(wiki_instructions.talent_lv)
    if not wiki_instructions.star and not wiki_instructions.talent_lv:
        wiki_instructions.skill = False
    return wiki_instructions


def set_common_character_attributes(wiki_instructions: WikiInstructions, character: Character) -> CharacterResponse:
    star = wiki_instructions.star
    char_response = CharacterResponse()
    if character.avatars is not None and len(character.avatars) > 0:
        char_response.avatar = character.avatars[random.randint(0, len(character.avatars) - 1)]
    else:
        char_response.avatar = None
    char_response.name = character.name
    char_response.star = star
    char_response.club = character.club
    char_response.hobbies = character.hobbies
    char_response.nicknames = character.nicknames
    if wiki_instructions.background:
        char_response.background = character.background
    char_response.type = character.type
    char_response.skins = character.skins
    char_response.extra = character.extra
    char_response.year = character.year
    char_response.element = character.element
    char_response.bonds = character.bonds
    char_response.tags = character.tags
    return char_response


def build_goodness_response(wiki_instructions: WikiInstructions, character: Character) -> CharacterResponse:
    """构建女神响应对象；女神无天赋、被动"""
    char_response = set_common_character_attributes(wiki_instructions, character)
    if char_response.star > 5:
        char_response.star = 5
    arena_skill_lv = char_response.star
    arena_skill_desc = character.arena_skill.descriptions[char_response.star - 1]
    char_response.arena_skill = CharacterResponse.Skill(
        name=character.arena_skill.name,
        lv=arena_skill_lv, desc=arena_skill_desc, cooldown=character.arena_skill.cooldown)

    if wiki_instructions.skin_order > 0:
        if character.skins is not None:
            skin = character.skins[min(wiki_instructions.skin_order, len(character.skins)) - 1]
            # 女神的皮肤有点区别，有被动技能
            skin_passive_skill = skin.get("passive_skill")
            skin_passive_skill_desc = skin_passive_skill.get("descriptions")
            skin_lv = min(wiki_instructions.skin_lv, len(skin_passive_skill_desc))
            skin_data = f"- {skin_passive_skill.get('name')}「lv{skin_lv}」: {skin_passive_skill_desc[skin_lv - 1]}"
            skin_images = skin.get("images")
            char_response.skin = {
                "name": skin.get('name'),
                "lv": skin_lv,
                "desc": skin_data,
                "image": skin_images[0] if len(skin_images) > 0 else ""
            }
    return char_response


def build_character_response(wiki_instructions: WikiInstructions, character: Character) -> CharacterResponse:
    if character.type == 2:
        return build_goodness_response(wiki_instructions, character)
    talent_lv = wiki_instructions.talent_lv
    char_response = set_common_character_attributes(wiki_instructions, character)
    # 星级大于5时才存在被动，并且是通常角色【女神最高5星】
    if char_response.star > 5:
        arena_skill_lv = 5
        # 当star大于5时，减5等于被动等级
        arena_skill_desc = character.arena_skill.descriptions[4]
        # 1、2年级，个别3年级无觉醒被动
        if character.awakening_passive is not None:
            awakening_passive_lv = char_response.star - 5
            awakening_passive_desc = character.awakening_passive.descriptions[awakening_passive_lv - 1]
            char_response.awakening_passive = CharacterResponse.Skill(
                name=character.awakening_passive.name,
                lv=awakening_passive_lv,
                desc=awakening_passive_desc, cooldown=None)
    else:
        arena_skill_lv = char_response.star
        arena_skill_desc = character.arena_skill.descriptions[char_response.star - 1]
    char_response.arena_skill = CharacterResponse.Skill(
        name=character.arena_skill.name,
        lv=arena_skill_lv, desc=arena_skill_desc, cooldown=character.arena_skill.cooldown)

    # 同上
    if character.talent_tree is not None:
        talent_tree_desc = character.talent_tree.descriptions[talent_lv - 1]
        char_response.talent_tree = CharacterResponse.Skill(
            name=character.talent_tree.name,
            lv=talent_lv,
            desc=talent_tree_desc, cooldown=None)

    # 处理被动技指令；
    # 目前只有一个，其他一些不涉及到数据显示的，不需要处理，如火刀被动加灼烧回合，但只存在于技能描述中，则不需要处理
    if char_response.awakening_passive is not None:
        awakening_passive_instructions = character.awakening_passive.instructions
        if awakening_passive_instructions and len(awakening_passive_instructions) > 0:
            for item in awakening_passive_instructions:
                if item.get('name') == "arena_skill_cooldown_reduction":
                    char_response.arena_skill.cooldown -= item.get('content')[char_response.awakening_passive.lv - 1]

    if wiki_instructions.skin_order > 0:
        if character.skins is not None:
            skin = character.skins[min(wiki_instructions.skin_order, len(character.skins)) - 1]
            skin_desc = skin.get("descriptions")
            skin_len = len(skin_desc)
            skin_data = skin_desc[min(wiki_instructions.skin_lv - 1, skin_len - 1)].split("\t")
            skin_lv = skin_data[0]
            skin_data = f"- 等级/攻击/血量/回复: lv{skin_lv}/{skin_data[1]}/{skin_data[2]}/{skin_data[3]}"
            skin_images = skin.get("images")
            char_response.skin = {
                "name": skin.get('name'),
                "lv": skin_lv,
                "desc": skin_data,
                "image": skin_images[0] if len(skin_images) > 0 else ""
            }

    return char_response


def build_help_guide() -> List[str]:
    """使用方式"""
    lines = ["「QTBot」使用指南"]
    lines.append("")
    lines.append("基础: 返回[角色]满星级&天赋数据")
    lines.append("")
    lines.append("- /查询 [角色]")
    lines.append("")
    lines.append("[角色]可以是游戏内(英文)名称，或任一已经录入的别名")
    lines.append("")
    lines.append("进阶: 返回[角色]指定参数的数据")
    lines.append("")
    lines.append('参数之间以半角"-"相连，可用的参数有，*星级*、*技能*、*皮肤*、*天赋*、*背景*。其中，'
                 '除了*背景*之外，其他可额外携带参数，以表示具体的等级、序号等，缺省时取默认值，每次最多携带3个')
    lines.append("")
    lines.append("[例如]")
    lines.append("")
    lines.append("1、九尾7星&天赋7&1号7级皮肤的数据")
    lines.append("/查询 九尾-7星-天赋7-皮肤1:7")
    lines.append("")
    lines.append("2、雅典娜3星&1号2级皮肤的数据")
    lines.append("/查询 雅典娜-3星-皮肤1:2")
    lines.append("")
    lines.append("3、雅典娜的背景故事")
    lines.append("/查询 雅典娜-背景")
    lines.append("")
    lines.append("翻译「机翻」:")
    lines.append("在[角色]之后，加上[:tl]参数可将文本翻译为中文")
    lines.append("")
    lines.append("[例如]")
    lines.append("/查询 雅典娜:tl")
    return lines
