from nonebot import on_command
from nonebot.adapters.qq import MessageSegment
from nonebot.params import CommandArg
from utils.common import build_help_guide


help_cmd = on_command("帮助", aliases={"help"}, priority=10, block=True)


@help_cmd.handle()
async def handle_help(args=CommandArg()):
    _input = args.extract_plain_text().strip()
    if not _input or _input == "帮助" or _input.lower() == "help":
        await help_cmd.finish(MessageSegment.text("\n".join(build_help_guide())))
