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
from services.character_service import CharacterService
import asyncio

super_cmd = on_command("su", aliases={"super"}, permission=SUPERUSER, priority=1, block=True)

running_tasks = {}


async def runner(
        event: Event,
        user_id,
        group_id,
        crawler: QTWikiCrawler, name_mapper: NameMapper, name, storage_service: StorageService):
    try:
        # 模拟耗时爬虫（实际替换成你的逻辑）
        result = await asyncio.to_thread(crawler.scrape_character_and_save, name)
        if result:
            message = f"[{name}]抓取成功"
            storage_service.sync_data_from_database(name)
            name_mapper.refresh_index()
        else:
            message = f"[{name}]抓取失败，详情请查看日志"
        logger.info(f"result: {message}")
        bot = get_bot()

        if group_id:
            at_message = f"{message}"
            await bot.send(event=event, message=at_message, at_sender=True)
        else:
            await bot.send(event=event, message=message, at_sender=True)
    except Exception as e:
        error_msg = f"失败: {str(e)[:100]}..."
        logger.exception(f"Scraping failed: {error_msg}")
        bot = get_bot()
        await bot.send(event=event, message="失败，请查看日志获取详细信息", at_sender=True)
    finally:
        running_tasks.pop(user_id, None)


async def runner2(
        event: Event,
        user_id,
        group_id,
        crawler: QTWikiCrawler,
        name_mapper: NameMapper, super_instructions, storage_service: StorageService):
    try:
        # 模拟耗时爬虫（实际替换成你的逻辑）
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
                    lines.append("- 推送成功")
                else:
                    lines.append("- 推送失败")
            else:
                lines.append("- 失败, 抓取到0条数据")
            if len(skip_names) > 0:
                lines.append(f"- 跳过[{', '.join(skip_names)}]")
        else:
            lines.append("失败，请查看日志获取详细信息")
        message = '\n'.join(lines)
        logger.info(f"result: {message}")
        bot = get_bot()

        if group_id:
            at_message = f"{message}"
            await bot.send(event=event, message=at_message, at_sender=True)
        else:
            await bot.send(event=event, message=message, at_sender=True)
    except Exception as e:
        error_msg = f"失败: {str(e)[:100]}..."
        logger.exception(f"Scraping failed: {error_msg}")
        bot = get_bot()
        if group_id:
            await bot.send(event=event, message="失败，请查看日志获取详细信息", at_sender=True)
        else:
            await bot.send(event=event, message=error_msg, at_sender=True)
    finally:
        running_tasks.pop(user_id, None)


async def runner3(event: Event, user_id, crawler: QTWikiCrawler, name: str, fields: str):
    try:
        result = await asyncio.to_thread(crawler.scrape_character_and_update_fields, name, fields.split(","))
        if result:
            message = "成功"
        else:
            message = "失败：请请查看日志获取详细信息"
        logger.info(f"result: {message}")
        bot = get_bot()
        await bot.send(event=event, message=message, at_sender=True)
    except Exception as e:
        error_msg = f"失败: {str(e)[:100]}..."
        logger.exception(f"Scraping failed: {error_msg}")
        bot = get_bot()
        await bot.send(event=event, message="失败，请查看日志获取详细信息", at_sender=True)
    finally:
        running_tasks.pop(user_id, None)


async def runner4(
        event: Event,
        user_id,
        group_id, storage_service: StorageService, name_mapper: NameMapper):
    try:
        # 模拟耗时爬虫（实际替换成你的逻辑）
        result = await asyncio.to_thread(storage_service.sync_data)
        if result:
            message = "成功"
            name_mapper.refresh_index()
        else:
            message = "失败：请请查看日志获取详细信息"
        logger.info(f"result: {message}")
        bot = get_bot()

        if group_id:
            at_message = f"{message}"
            await bot.send(event=event, message=at_message, at_sender=True)
        else:
            await bot.send(event=event, message=message, at_sender=True)
    except Exception as e:
        error_msg = f"失败: {str(e)[:100]}..."
        logger.exception(f"Scraping failed: {error_msg}")
        bot = get_bot()
        if group_id:
            await bot.send(event=event, message="失败，请查看日志获取详细信息", at_sender=True)
        else:
            await bot.send(event=event, message=error_msg, at_sender=True)
    finally:
        running_tasks.pop(user_id, None)


# async def runner5(
#         event: Event,
#         user_id,
#         group_id, storage_service: StorageService, character: dict):
#     try:
#         # 模拟耗时爬虫（实际替换成你的逻辑）
#         result = await asyncio.to_thread(storage_service.push_characters, [character])
#         if result:
#             message = "成功"
#         else:
#             message = "失败：请请查看日志获取详细信息"
#         logger.info(f"result: {message}")
#         bot = get_bot()
#
#         if group_id:
#             at_message = f"{message}"
#             await bot.send(event=event, message=at_message, at_sender=True)
#         else:
#             await bot.send(event=event, message=message, at_sender=True)
#     except Exception as e:
#         error_msg = f"失败: {str(e)[:100]}..."
#         logger.exception(f"Scraping failed: {error_msg}")
#         bot = get_bot()
#         await bot.send(event=event, message="失败，请查看日志获取详细信息", at_sender=True)
#     finally:
#         running_tasks.pop(user_id, None)


async def runner6(event, user_id, storage_service: StorageService, name: str):
    try:
        result = await asyncio.to_thread(storage_service.sync_data_from_database, name)
        if result:
            message = "成功"
        else:
            message = "失败：请请查看日志获取详细信息"
        logger.info(f"result: {message}")
        bot = get_bot()
        await bot.send(event=event, message=message, at_sender=True)
    except Exception as e:
        error_msg = f"失败: {str(e)[:100]}..."
        logger.exception(f"Scraping failed: {error_msg}")
        bot = get_bot()
        await bot.send(event=event, message="失败，请查看日志获取详细信息", at_sender=True)
    finally:
        running_tasks.pop(user_id, None)


@super_cmd.handle()
async def handle_super(event: Event, args=CommandArg()):
    user_id = event.get_user_id()
    group_id = None
    if hasattr(event, 'group_id'):
        group_id = str(event.group_id)
    _input = args.extract_plain_text().strip()
    if not _input:
        await super_cmd.finish("请输入指令")
    container = get_container()
    storage_service = cast(StorageService, container.storage_service())
    name_mapper = cast(NameMapper, container.name_mapper())
    crawler = cast(QTWikiCrawler, container.qt_wiki_crawler())
    character_service = cast(CharacterService, container.character_service())
    if _input == "刷新索引":
        name_mapper.refresh_index()
        await super_cmd.finish("成功")
    elif _input == "同步至数据库":
        if user_id in running_tasks and not running_tasks[user_id].done():
            await super_cmd.finish("任务正在进行，请勿重复提交")
        await super_cmd.send(f"正在同步数据，请稍候...")
        task = asyncio.create_task(
            runner4(event, user_id, group_id, name_mapper=name_mapper, storage_service=storage_service)
        )
        running_tasks[user_id] = task
    elif _input.startswith("抓取更新:"):
        instructions = _input[3:].split(":")
        if len(instructions) != 2:
            await super_cmd.finish("指令格式错误")

        name = instructions[0]
        fields = instructions[1]
        canonical_name = name_mapper.get_canonical_name(name)
        if not canonical_name:
            await super_cmd.finish(f"未查找到[{name}]的数据")
        await super_cmd.send(f"后台执行中，请稍候...")
        task = asyncio.create_task(
            runner3(
                event,
                user_id,
                crawler=crawler, name=canonical_name, fields=fields)
        )
        running_tasks[user_id] = task
    elif _input.startswith("抓取"):
        # ✅ 启动后台任务（不阻塞）
        super_instructions = parse_super_instructions(_input)
        if super_instructions.count > 0:
            await super_cmd.send(f"后台执行中，请稍候...")
            task = asyncio.create_task(
                runner2(
                    event=event,
                    user_id=user_id, group_id=group_id, crawler=crawler, name_mapper=name_mapper,
                    super_instructions=super_instructions, storage_service=storage_service)
            )
            running_tasks[user_id] = task
        else:
            canonical_name = name_mapper.get_canonical_name(super_instructions.char_name)
            if canonical_name:
                await super_cmd.finish(f"角色[{canonical_name}]数据已存在")
            logger.info(f"开始抓取[{canonical_name}]...")
            if user_id in running_tasks and not running_tasks[user_id].done():
                await super_cmd.finish("任务正在进行，请勿重复提交")
            await super_cmd.send(f"正在抓取「{super_instructions.char_name}」条目，请稍候...")
            logger.info("后台执行...")
            task = asyncio.create_task(runner(
                event,
                user_id,
                group_id, crawler, name_mapper, name=super_instructions.char_name, storage_service=storage_service))
            running_tasks[user_id] = task
    elif _input.startswith("同步至外部存储:"):
        name = _input[8:]
        if not name:
            await super_cmd.finish("请输入需要推送的角色名称")
        canonical_name = name_mapper.get_canonical_name(name)
        if not canonical_name:
            await super_cmd.finish(f"未查找到[{name}]的数据")
        task = asyncio.create_task(
            runner6(event, user_id, storage_service=storage_service, name=canonical_name)
        )
        running_tasks[user_id] = task
    # elif _input.startswith("推送:"):
    #     name = _input[3:]
    #     if not name:
    #         await super_cmd.finish("请输入需要推送的角色名称")
    #     canonical_name = name_mapper.get_canonical_name(name)
    #     if not canonical_name:
    #         await super_cmd.finish(f"未查找到[{name}]的数据")
    #     await super_cmd.send(f"推送中，请稍候...")
    #     character = character_service.get_character_by_name(name=canonical_name, data_type=2)
    #     if not character:
    #         await super_cmd.finish(f"未查找到[{name}]的数据，请录入")
    #     task = asyncio.create_task(
    #         runner5(
    #             event,
    #             user_id,
    #             group_id,
    #             storage_service=storage_service, character=character)
    #     )
    #     running_tasks[user_id] = task
    else:
        await super_cmd.finish("未知指令")
