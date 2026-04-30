from nonebot.permission import SUPERUSER
from nonebot import on_command, get_bot, logger
from nonebot.params import CommandArg, Depends
from nonebot.adapters import Event

from containers.app_container import container
from runner.su_runner import SuperRunner
from constants.message import *
from nonebot.adapters.qq import MessageSegment
from utils.common import build_super_guide

super_cmd = on_command("su", aliases={"super"}, permission=SUPERUSER, priority=1, block=True)
running_tasks = {}


def get_super_runner() -> SuperRunner:
    return container.super_runner()


def callback(event: Event, user_id):
    """异步回调；包含闭包"""
    async def inner(error, message):
        bot = get_bot()
        if error:
            logger.exception(f"error: {error}")
            await bot.send(event=event, message=execution_error, at_sender=True)
        else:
            logger.info(f"message: {message}")
            running_tasks.pop(user_id, None)
            await bot.send(event=event, message=message, at_sender=True)
    return inner


@super_cmd.handle()
async def handle_super(event: Event, args=CommandArg(), super_runner: SuperRunner = Depends(get_super_runner)):
    user_id = event.get_user_id()
    _input = args.extract_plain_text().strip()

    if not _input or _input == "帮助" or _input.lower() == "help":
        await super_cmd.finish(MessageSegment.text("\n".join(build_super_guide())))
    if user_id in running_tasks and not running_tasks[user_id].done():
        await super_cmd.finish(repeated_instruction_error)
    await super_runner.run(
        _input=_input, running_tasks=running_tasks,
        super_cmd=super_cmd, callback=callback,
        event=event,
        user_id=user_id,
        logger=logger
    )
