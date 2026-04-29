import asyncio

from constants.message import success, background_execution, background_sync, execution_error, instruction_error, \
    no_character_name_error, not_supported
from services.qt_wiki_crawler import QTWikiCrawler
from nonebot.adapters import Event
from utils.common import parse_super_instructions


class SuperRunner:

    def __init__(self, qt_wiki_crawler: QTWikiCrawler, storage_service, name_mapper):
        self.crawler = qt_wiki_crawler
        self.storage_service = storage_service
        self.name_mapper = name_mapper

    async def run(self, _input: str, super_cmd, logger, callback, running_tasks, event: Event, user_id):
        task = None
        if _input == "刷新索引":
            self.name_mapper.refresh_index()
            await super_cmd.finish(success)
        elif _input.startswith("抓取最新数据"):
            await super_cmd.send(f"正在抓取「最新数据」条目，请稍候...")
            logger.info(background_execution)
            task = asyncio.create_task(self.get_latest(callback=callback(event, user_id)))
        elif _input == "同步至数据库":
            await super_cmd.send(background_sync)
            task = asyncio.create_task(self.sync_local2database(callback=callback(event, user_id)))
        elif _input.startswith("更新:"):
            instructions = _input[5:].split(":")
            if len(instructions) != 2:
                await super_cmd.finish(instruction_error)
            name = instructions[0]
            fields = instructions[1]
            canonical_name = self.name_mapper.get_canonical_name(name)
            if not canonical_name:
                await super_cmd.finish(f"未查找到[{name}]的数据")
            await super_cmd.send(background_execution)
            task = asyncio.create_task(
                self.update_character(
                    callback=callback(event, user_id),
                    name=canonical_name,
                    fields=fields)
            )
        elif _input.startswith("同步至外部存储:"):
            name = _input[8:]
            if not name:
                await super_cmd.finish(no_character_name_error)
            canonical_name = self.name_mapper.get_canonical_name(name)
            if not canonical_name:
                await super_cmd.finish(f"未查找到[{name}]的数据")
            task = asyncio.create_task(
                self.sync_database2local(callback=callback(event, user_id), name=canonical_name)
            )
        elif _input.startswith("抓取"):
            super_instructions = parse_super_instructions(_input)
            if super_instructions.count > 0:
                await super_cmd.send(background_execution)
                task = asyncio.create_task(
                    self.get_characters(
                        callback=callback(event, user_id),
                        super_instructions=super_instructions)
                )
        if task:
            running_tasks[user_id] = task

    async def get_latest(self, callback):
        """抓取最新数据"""
        error_message = None
        message = None
        try:
            result = await asyncio.to_thread(self.crawler.scrape_latest_character)
            names = result.get("names") if result else None
            if names and len(names) == 1:
                message = f"[{names[0]}]抓取成功"
                self.name_mapper.refresh_index()
            else:
                message = f"[{result}]抓取失败，详情请查看日志"
        except Exception as e:
            error_message = f"失败: {str(e)[:100]}..."
        finally:
            # 通过回调传信息
            await callback(error_message, message)

    async def sync_local2database(self, callback):
        """同步本地数据至数据库"""
        error_message = None
        message = None
        try:
            result = await asyncio.to_thread(self.storage_service.sync_data)
            if result > 1:
                message = success
                self.name_mapper.refresh_index()
            elif result == 1:
                message = "无需更新"
            else:
                message = execution_error
        except Exception as e:
            error_message = f"失败: {str(e)[:100]}..."
        finally:
            await callback(error_message, message)

    async def update_character(self, callback, name, fields):
        """更新角色"""
        error_message = None
        message = None
        try:
            result = await asyncio.to_thread(self.crawler.scrape_character_and_update_fields, name, fields.split(","))
            message = success if result else execution_error
        except Exception as e:
            error_message = f"失败: {str(e)[:100]}..."
        finally:
            await callback(error_message, message)

    async def get_characters(self, callback, super_instructions):
        """抓取角色"""
        error_message = None
        message = None
        try:
            result = await asyncio.to_thread(self.crawler.run, scrape_instructions=super_instructions)
            lines = []
            if result:
                names = result['names']
                skip_names = result['skip_names']
                lines = []
                names_len = len(names)
                lines.append("结果：")
                if names_len > 0:
                    lines.append(f"- 抓取到[{', '.join(names)}]条目, 共{names_len}个")
                    self.name_mapper.refresh_index()
                else:
                    lines.append("- 失败, 抓取到0条数据")
                if len(skip_names) > 0:
                    lines.append(f"- 跳过[{', '.join(skip_names)}]")
            else:
                lines.append(execution_error)
            message = '\n'.join(lines)
        except Exception as e:
            error_message = f"失败: {str(e)[:100]}..."
        finally:
            await callback(error_message, message)

    async def sync_database2local(self, callback, name: str):
        """同步数据库至外部存储"""
        error_message = None
        message = None
        try:
            result = await asyncio.to_thread(self.storage_service.sync_data_from_database, name)
            if result == -1:
                message = not_supported
            else:
                message = success if result else execution_error
        except Exception as e:
            error_message = f"失败: {str(e)[:100]}..."
        finally:
            await callback(error_message, message)
