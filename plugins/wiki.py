from nonebot import on_command
from nonebot.adapters.qq import MessageSegment
from nonebot.params import CommandArg
from typing import cast
from services.character_service import CharacterService
from services.translation_service import TranslationService
from utils.name_mapper import NameMapper
from containers.global_conf import get_container
from utils.common import parse_instructions, build_character_response, build_help_guide
from utils.message_helper import build_markdown_content


# Wiki 查询命令
wiki_cmd = on_command("百科", aliases={"查询", "info", "wiki"}, priority=10, block=True)


@wiki_cmd.handle()
async def handle_wiki(args=CommandArg()):
    _input = args.extract_plain_text().strip()
    container = get_container()
    name_mapper = cast(NameMapper, container.name_mapper())
    character_service = cast(CharacterService, container.character_service())

    if not _input or _input == "帮助" or _input.lower() == "help":
        await wiki_cmd.finish(MessageSegment.text("\n".join(build_help_guide())))
    # 拆分指令；指令应该以角色名称开头，如：火棍-7星-天赋10，火棍-背景
    instructions = parse_instructions(_input)
    # 需要输入精准名称，不支持模糊查询，但是提供配置别名
    canonical_name = name_mapper.get_canonical_name(instructions.name)
    if not canonical_name:
        await wiki_cmd.finish(MessageSegment.text(f"未查找到[{instructions.name}]的数据，请通知管理员录入"))
    character = character_service.get_character_by_name(canonical_name)
    if not character:
        await wiki_cmd.finish(MessageSegment.text(f"未查找到[{canonical_name}]的数据，请通知管理员录入"))

    character_response = build_character_response(wiki_instructions=instructions, character=character)
    if instructions.tl and character.translated != 1:
        translation_service = cast(TranslationService, container.translation_service())
        translation_service.translate_character(character_response)
    markdown_content = build_markdown_content(wiki_instructions=instructions, character_response=character_response)
    # await wiki_cmd.finish(MessageSegment.markdown("\n".join(markdown_content)))
    markdown_content = "\n".join(markdown_content)
    await wiki_cmd.finish(MessageSegment.text(markdown_content))
