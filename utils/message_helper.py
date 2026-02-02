from typing import List

from bo.wiki_instructions import WikiInstructions
from vo.character_response import CharacterResponse


def build_markdown_content(wiki_instructions: WikiInstructions, character_response: CharacterResponse) -> List[str]:
    show_background = wiki_instructions.background
    character_type = character_response.type
    lines = []
    lines.append(
        f"{character_response.name}「{character_response.star}★」"
        if wiki_instructions.star > 0
        else character_response.name)
    lines.append("")
    if character_response.avatar:
        # lines.append(f"![avatar]({character_response.avatar})")
        lines.append(f"![avatar](图)")
        lines.append("")

    if character_response.nicknames:
        lines.append(f"别名: {character_response.nicknames}")
    if character_type == 1:
        tags = f"标签: {character_response.club}, {character_response.year}年级, {character_response.element}"
    else:
        tags = f"标签: {character_response.club}, 女神"
    if character_response.tags and len(character_response.tags) > 0:
        tags += ", " + ", ".join(character_response.tags)
    lines.append(tags)
    if character_response.hobbies:
        lines.append(f"爱好: {character_response.hobbies}")
    if character_response.extra:
        if 'birthday' in character_response.extra:
            lines.append(f"生日: {character_response.extra['birthday']}")
        sub_title = ""
        content = ""
        if 'height' in character_response.extra:
            sub_title += "身高"
            content += str(character_response.extra['height'])
        if 'weight' in character_response.extra:
            sub_title += "/体重"
            content += f"/{character_response.extra['weight']}"
        if 'body_size' in character_response.extra:
            sub_title += "/三围"
            content += f"/{character_response.extra['body_size']}"
        if sub_title != '':
            lines.append(f"{sub_title}: {content}")
    if character_response.bonds:
        lines.append(f"羁绊: {character_response.bonds}")

    if character_response.skins is not None:
        content = ", ".join(f"{i}-{item['name']}" for i, item in enumerate(character_response.skins, start=1))
        lines.append(f"皮肤: {content}")
    if wiki_instructions.star > 0:
        lines.append("")
        lines.append(f"主动技: {character_response.arena_skill.name}「lv{character_response.arena_skill.lv}」| 冷却: {character_response.arena_skill.cooldown}")
        lines.append("")
        lines.append(character_response.arena_skill.desc)
        # 通常角色
        if character_type == 1:
            if character_response.awakening_passive is not None:
                lines.append("")
                lines.append(f"觉醒被动: {character_response.awakening_passive.name}「lv{character_response.awakening_passive.lv}」")
                lines.append("")
                lines.append(character_response.awakening_passive.desc)
    if wiki_instructions.talent_lv > 0:
        if character_type == 1 and character_response.talent_tree is not None:
            lines.append("")
            lines.append(f"天赋: {character_response.talent_tree.name}「lv{character_response.talent_tree.lv}」")
            lines.append("")
            lines.append(character_response.talent_tree.desc)
    if show_background:
        lines.append("")
        lines.append("背景故事: ")
        lines.append("")
        lines.append(character_response.background)

    if character_response.skin:
        lines.append("")
        lines.append(f"[皮肤]: {wiki_instructions.skin_order}-{character_response.skin.get('name')}")
        lines.append("")
        if character_response.skin.get("image"):
            lines.append(f"![skin](图)")
            lines.append("")
        lines.append(character_response.skin.get("desc"))
    return lines
