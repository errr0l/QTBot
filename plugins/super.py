from typing import cast

from nonebot.permission import SUPERUSER
from nonebot import on_command, get_bot, logger
from nonebot.params import CommandArg
from nonebot.adapters import Event
from containers.global_conf import get_container
from services.qt_wiki_crawler import QTWikiCrawler
from utils.name_mapper import NameMapper
from utils.common import parse_super_instructions
from services.google_sheets_service import GoogleSheetsService
from services.character_service import CharacterService
import asyncio

super_cmd = on_command("su", aliases={"super"}, permission=SUPERUSER, priority=1, block=True)

running_tasks = {}


async def runner(event: Event, user_id, group_id, crawler: QTWikiCrawler, name_mapper: NameMapper, name):
    try:
        # 模拟耗时爬虫（实际替换成你的逻辑）
        result = await asyncio.to_thread(crawler.scrape_character_and_save, name)
        if result:
            message = f"[{name}]抓取成功"
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
        await bot.send(event=event, message=error_msg, at_sender=True)
    finally:
        running_tasks.pop(user_id, None)


async def runner2(
        event: Event,
        user_id,
        group_id,
        crawler: QTWikiCrawler,
        name_mapper: NameMapper, super_instructions, google_sheets_service: GoogleSheetsService):
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
                    google_sheets_service.push_characters_to_google_sheets,
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


# async def runner3(event: Event, user_id, group_id, crawler: QTWikiCrawler, name_mapper: NameMapper, name):
#     try:
#         result = await asyncio.to_thread(crawler.scrape_character_and_update, name)
#         if result:
#             message = f"[{name}]更新成功"
#             name_mapper.refresh_index()
#         else:
#             message = f"[{name}]更新失败，详情请查看日志"
#         logger.info(f"result: {message}")
#         bot = get_bot()
#
#         if group_id:
#             at_message = f"{message}"
#             await bot.send(event=event, message=at_message, at_sender=True)
#         else:
#             await bot.send(event=event, message=message,at_sender=True)
#     except Exception as e:
#         error_msg = f"失败: {str(e)[:100]}..."
#         logger.exception(f"{error_msg}")
#         bot = get_bot()
#         await bot.send(event=event, message="失败，请查看日志获取详细信息", at_sender=True)
#     finally:
#         running_tasks.pop(user_id, None)

async def runner4(
        event: Event,
        user_id,
        group_id, google_sheets_service: GoogleSheetsService, name_mapper: NameMapper):
    try:
        # 模拟耗时爬虫（实际替换成你的逻辑）
        result = await asyncio.to_thread(google_sheets_service.sync_data)
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


async def runner5(
        event: Event,
        user_id,
        group_id, google_sheets_service: GoogleSheetsService, character: dict):
    try:
        # 模拟耗时爬虫（实际替换成你的逻辑）
        result = await asyncio.to_thread(google_sheets_service.push_characters_to_google_sheets, [character])
        if result:
            message = "成功"
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


@super_cmd.handle()
async def handle_super(event: Event, args=CommandArg()):
    user_id = event.get_user_id()
    group_id = None
    if hasattr(event, 'group_id'):
        group_id = str(event.group_id)
    _input = args.extract_plain_text().strip()
    if _input == "刷新索引":
        container = get_container()
        name_mapper = cast(NameMapper, container.name_mapper())
        name_mapper.refresh_index()
        await super_cmd.finish("成功")
    elif _input.startswith("抓取"):
        # ✅ 启动后台任务（不阻塞）
        super_instructions = parse_super_instructions(_input)
        container = get_container()
        name_mapper = cast(NameMapper, container.name_mapper())
        crawler = cast(QTWikiCrawler, container.qt_wiki_crawler())
        if super_instructions.count > 0:
            await super_cmd.send(f"后台执行中，请稍候...")
            task = asyncio.create_task(
                runner2(
                    event=event,
                    user_id=user_id, group_id=group_id, crawler=crawler, name_mapper=name_mapper,
                    super_instructions=super_instructions)
            )
            running_tasks[user_id] = task
        else:
            name_mapper = cast(NameMapper, container.name_mapper())
            canonical_name = name_mapper.get_canonical_name(super_instructions.char_name)
            if canonical_name:
                await super_cmd.finish(f"角色[{canonical_name}]数据已存在")
            logger.info(f"开始抓取[{canonical_name}]...")
            if user_id in running_tasks and not running_tasks[user_id].done():
                await super_cmd.finish("任务正在进行，请勿重复提交")
            await super_cmd.send(f"正在抓取「{super_instructions.char_name}」条目，请稍候...")
            logger.info("后台执行...")
            task = asyncio.create_task(
                runner(event, user_id, group_id, crawler, name_mapper, name=super_instructions.char_name)
            )
            running_tasks[user_id] = task
    elif _input == "同步数据":
        if user_id in running_tasks and not running_tasks[user_id].done():
            await super_cmd.finish("任务正在进行，请勿重复提交")
        await super_cmd.send(f"正在同步数据，请稍候...")
        container = get_container()
        google_sheets_service = cast(GoogleSheetsService, container.google_sheets_service())
        name_mapper = cast(NameMapper, container.name_mapper())
        task = asyncio.create_task(
            runner4(event, user_id, group_id, name_mapper=name_mapper, google_sheets_service=google_sheets_service)
        )
        running_tasks[user_id] = task
    elif _input.startswith("推送:"):
        name = _input[3:]
        if not name:
            await super_cmd.finish("请输入需要推送的角色名称")
        container = get_container()
        name_mapper = cast(NameMapper, container.name_mapper())
        canonical_name = name_mapper.get_canonical_name(name)
        if not canonical_name:
            await super_cmd.finish(f"未查找到[{name}]的数据")
        await super_cmd.send(f"推送中，请稍候...")
        google_sheets_service = cast(GoogleSheetsService, container.google_sheets_service())
        character_service = cast(CharacterService, container.character_service())
        character = character_service.get_character_by_name(name=canonical_name, data_type=2)
        if not character:
            await super_cmd.finish(f"未查找到[{name}]的数据，请录入")
        task = asyncio.create_task(
            runner5(
                event,
                user_id,
                group_id,
                google_sheets_service=google_sheets_service, character=character)
        )
        running_tasks[user_id] = task
    # elif _input.startswith("更新"):
    #     super_instructions = parse_super_instructions(_input)
    #     container = get_container()
    #     name_mapper = cast(NameMapper, container.name_mapper())
    #     canonical_name = name_mapper.get_canonical_name(super_instructions.char_name)
    #     if not canonical_name:
    #         await super_cmd.finish(f"角色[{canonical_name}]数据不存在")
    #     if user_id in running_tasks and not running_tasks[user_id].done():
    #         await super_cmd.finish("任务正在进行，请勿重复提交")
    #     crawler = cast(QTWikiCrawler, container.qt_wiki_crawler())
    #     task = asyncio.create_task(
    #         runner3(event, user_id, group_id, crawler, name_mapper, name=canonical_name)
    #     )
    #     running_tasks[user_id] = task
    else:
        await super_cmd.finish("未知指令")
