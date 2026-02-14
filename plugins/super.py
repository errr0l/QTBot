from typing import cast

from nonebot.permission import SUPERUSER
from nonebot import on_command, get_bot, logger
from nonebot.params import CommandArg
from nonebot.adapters import Event
from containers.global_conf import get_container
from services.qt_wiki_crawler import QTWikiCrawler
from utils.name_mapper import NameMapper
from utils.common import parse_super_instructions
from services.storage_service import StorageService
import asyncio
from constants.message import *

super_cmd = on_command("su", aliases={"super"}, permission=SUPERUSER, priority=1, block=True)

running_tasks = {}


async def runner(
        event: Event, user_id, crawler: QTWikiCrawler, name_mapper: NameMapper, name, storage_service: StorageService):
    try:
        result = await asyncio.to_thread(crawler.scrape_character_and_save, name)
        if result:
            message = f"[{name}]抓取成功"
            storage_service.sync_data_from_database(name)
            name_mapper.refresh_index()
        else:
            message = f"[{name}]抓取失败，详情请查看日志"
        logger.info(f"result: {message}")
        bot = get_bot()

        await bot.send(event=event, message=message, at_sender=True)
    except Exception as e:
        error_msg = f"失败: {str(e)[:100]}..."
        logger.exception(f"error: {error_msg}")
        bot = get_bot()
        await bot.send(event=event, message=execution_error, at_sender=True)
    finally:
        running_tasks.pop(user_id, None)


async def runner2(
        event: Event,
        user_id,
        crawler: QTWikiCrawler,
        name_mapper: NameMapper, super_instructions, storage_service: StorageService):
    try:
        result = await asyncio.to_thread(crawler.run, scrape_instructions=super_instructions)
        lines = []
        if result:
            names = result['names']
            skip_names = result['skip_names']
            logger.info(names)
            lines = []
            names_len = len(names)
            characters = result['characters']

            lines.append("结果：")
            if names_len > 0:
                lines.append(f"- 抓取到[{', '.join(names)}]条目, 共{names_len}个")
                name_mapper.refresh_index()
                push_result = await asyncio.to_thread(
                    storage_service.sync_data_from_list,
                    [char.to_dict() for char in characters]
                )
                if push_result:
                    lines.append("- 已同步")
                else:
                    lines.append("- 同步失败")
            else:
                lines.append("- 失败, 抓取到0条数据")
            if len(skip_names) > 0:
                lines.append(f"- 跳过[{', '.join(skip_names)}]")
        else:
            lines.append(execution_error)
        message = '\n'.join(lines)
        logger.info(f"result: {message}")
        bot = get_bot()

        await bot.send(event=event, message=message, at_sender=True)
    except Exception as e:
        error_msg = f"失败: {str(e)[:100]}..."
        logger.exception(f"error: {error_msg}")
        bot = get_bot()
        await bot.send(event=event, message=execution_error, at_sender=True)
    finally:
        running_tasks.pop(user_id, None)


async def runner3(
        event: Event, user_id, storage_service: StorageService, crawler: QTWikiCrawler, name: str, fields: str):
    try:
        result = await asyncio.to_thread(crawler.scrape_character_and_update_fields, name, fields.split(","))
        sync_result = storage_service.sync_data_from_dict(result)
        message = success if sync_result else execution_error
        logger.info(f"result: {message}")
        bot = get_bot()
        await bot.send(event=event, message=message, at_sender=True)
    except Exception as e:
        error_msg = f"失败: {str(e)[:100]}..."
        logger.exception(f"error: {error_msg}")
        bot = get_bot()
        await bot.send(event=event, message=execution_error, at_sender=True)
    finally:
        running_tasks.pop(user_id, None)


async def runner4(
        event: Event,
        user_id, storage_service: StorageService, name_mapper: NameMapper):
    try:
        result = await asyncio.to_thread(storage_service.sync_data)
        if result > 1:
            message = success
            name_mapper.refresh_index()
        else:
            message = "无需更新"
        logger.info(f"result: {message}")
        bot = get_bot()

        await bot.send(event=event, message=message, at_sender=True)
    except Exception as e:
        error_msg = f"失败: {str(e)[:100]}..."
        logger.exception(f"error: {error_msg}")
        bot = get_bot()
        await bot.send(event=event, message=execution_error, at_sender=True)
    finally:
        running_tasks.pop(user_id, None)


async def runner6(event, user_id, storage_service: StorageService, name: str):
    try:
        result = await asyncio.to_thread(storage_service.sync_data_from_database, name)
        message = success if result else execution_error
        logger.info(f"message: {message}")
        bot = get_bot()
        await bot.send(event=event, message=message, at_sender=True)
    except Exception as e:
        error_msg = f"失败: {str(e)[:100]}..."
        logger.exception(f"error: {error_msg}")
        bot = get_bot()
        await bot.send(event=event, message=execution_error, at_sender=True)
    finally:
        running_tasks.pop(user_id, None)


@super_cmd.handle()
async def handle_super(event: Event, args=CommandArg()):
    user_id = event.get_user_id()
    _input = args.extract_plain_text().strip()
    if not _input:
        await super_cmd.finish(no_instruction_error)
    if user_id in running_tasks and not running_tasks[user_id].done():
        await super_cmd.finish(repeated_instruction_error)
    container = get_container()
    storage_service = cast(StorageService, container.storage_service())
    name_mapper = cast(NameMapper, container.name_mapper())
    crawler = cast(QTWikiCrawler, container.qt_wiki_crawler())
    if _input == "刷新索引":
        name_mapper.refresh_index()
        await super_cmd.finish(success)
    elif _input == "同步至数据库":
        await super_cmd.send(background_sync)
        task = asyncio.create_task(
            runner4(event, user_id, name_mapper=name_mapper, storage_service=storage_service)
        )
        running_tasks[user_id] = task
    elif _input.startswith("抓取更新:"):
        instructions = _input[5:].split(":")
        if len(instructions) != 2:
            await super_cmd.finish(instruction_error)

        name = instructions[0]
        fields = instructions[1]
        canonical_name = name_mapper.get_canonical_name(name)
        if not canonical_name:
            await super_cmd.finish(f"未查找到[{name}]的数据")
        await super_cmd.send(background_execution)
        task = asyncio.create_task(
            runner3(
                event,
                user_id,
                storage_service=storage_service,
                crawler=crawler, name=canonical_name, fields=fields)
        )
        running_tasks[user_id] = task
    elif _input.startswith("抓取"):
        # ✅ 启动后台任务（不阻塞）
        super_instructions = parse_super_instructions(_input)
        if super_instructions.count > 0:
            await super_cmd.send(background_execution)
            task = asyncio.create_task(
                runner2(
                    event=event,
                    user_id=user_id, crawler=crawler, name_mapper=name_mapper,
                    super_instructions=super_instructions, storage_service=storage_service)
            )
            running_tasks[user_id] = task
        else:
            canonical_name = name_mapper.get_canonical_name(super_instructions.char_name)
            if canonical_name:
                await super_cmd.finish(f"角色[{canonical_name}]数据已存在")
            logger.info(f"开始抓取[{canonical_name}]...")
            await super_cmd.send(f"正在抓取「{super_instructions.char_name}」条目，请稍候...")
            logger.info(background_execution)
            task = asyncio.create_task(runner(
                event,
                user_id, crawler, name_mapper, name=super_instructions.char_name, storage_service=storage_service))
            running_tasks[user_id] = task
    elif _input.startswith("同步至外部存储:"):
        name = _input[8:]
        if not name:
            await super_cmd.finish(no_character_name_error)
        canonical_name = name_mapper.get_canonical_name(name)
        if not canonical_name:
            await super_cmd.finish(f"未查找到[{name}]的数据")
        task = asyncio.create_task(
            runner6(event, user_id, storage_service=storage_service, name=canonical_name)
        )
        running_tasks[user_id] = task
    else:
        await super_cmd.finish(unknown_instruction)
