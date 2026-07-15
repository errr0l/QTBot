from nonebot import on_command, on_message
from nonebot.adapters.qq import MessageSegment
from nonebot.params import CommandArg
from nonebot.adapters import Event
from typing import cast

from containers.app_container import container
from services.character_service import CharacterService
from services.translation_service import TranslationService
from utils.name_mapper import NameMapper
from utils.common import parse_instructions, build_character_response, build_user_guide, build_character_overview
from utils.message_helper import build_markdown_content


# Wiki 查询命令
wiki_cmd = on_command("百科", aliases={"查询", "wiki"}, priority=10, block=True)


async def _query_character(input_text: str) -> str:
    """执行百科查询，返回格式化后的响应文本"""

    if not input_text or input_text == "帮助":
        await wiki_cmd.finish(MessageSegment.text("\n".join(build_user_guide())))
    name_mapper = cast(NameMapper, container.name_mapper())
    if input_text == "角色":
        lines = build_character_overview(name_mapper.get_alia4characters())
        await wiki_cmd.finish(MessageSegment.text("\n".join(lines)))
    if input_text == '女神':
        lines = build_character_overview(name_mapper.get_alia4goddesses())
        await wiki_cmd.finish(MessageSegment.text("\n".join(lines)))
    character_service = cast(CharacterService, container.character_service())
    instructions = parse_instructions(input_text)
    canonical_name = name_mapper.get_canonical_name(instructions.name)
    if not canonical_name:
        suggestions = name_mapper.fuzzy_search(instructions.name)
        if suggestions:
            return f"未找到「{instructions.name}」，你是不是想找：\n" + "\n".join(f"- {s}" for s in suggestions)
        return f"未查找到[{instructions.name}]的数据，请通知管理员录入"
    character = character_service.get_character_by_name(canonical_name)
    if not character:
        return f"未查找到[{canonical_name}]的数据，请通知管理员录入"

    character_response = build_character_response(wiki_instructions=instructions, character=character)
    if instructions.tl and character.translated != 1:
        translation_service = cast(TranslationService, container.translation_service())
        translation_service.translate_character(character_response)
    markdown_content = build_markdown_content(wiki_instructions=instructions, character_response=character_response)
    return "\n".join(markdown_content)


@wiki_cmd.handle()
async def handle_wiki(args=CommandArg()):
    _input = args.extract_plain_text().strip()
    result = await _query_character(_input)
    await wiki_cmd.finish(MessageSegment.text(result))


# 兜底处理：非命令消息当作百科查询处理
fallback = on_message(priority=100, block=False)


@fallback.handle()
async def handle_fallback(event: Event):
    text = event.get_plaintext().strip()
    result = await _query_character(text)
    await fallback.finish(MessageSegment.text(result))
