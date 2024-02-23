import asyncio
from crawl import SearchPost, SearchUser, Update
import time
from utils.logger import logger
import psutil
import config.config as cfg
from playwright.async_api import async_playwright
from process_data import *
from config.get_config import read_config

class TaskManager:
    def __init__(self):
        self.active_tasks = {}

    async def process_task(self, config_id, config):
        while True:
            print(f"Process task id: {config_id}...")
            mode = config["mode"]["id"]
            if mode == 3:
                logger.debug("Mode search user")
                crawl = SearchUser(config=config)
            if mode == 4:
                logger.debug("Mode search posts")
                crawl = SearchPost(config=config)
            if mode == 5:
                logger.debug("Mode update")
                crawl = Update(config=config)
            await crawl.run()
            await asyncio.sleep(1)

    async def check_config_file(self):
        while True:
            ### Read config
            list_config_data = read_config()
            config_ids = []
            for config in list_config_data:
                config_id = config.get("id")
                config_ids.append(config_id)
                if config_id not in self.active_tasks.keys():
                    logger.debug(f"Create new task for id: {config_id}")
                    task = asyncio.create_task(self.process_task(config_id, config))
                    self.active_tasks[config_id] = task
                    # await task
            completed_tasks = list(set(self.active_tasks.keys()) - set(config_ids))
            for task_id in completed_tasks:
                logger.debug(f"Cancel task ID: {task_id}")
                task = self.active_tasks.pop(task_id)
                task.cancel()
                try:
                    await asyncio.shield(asyncio.wait([task]))
                except asyncio.CancelledError:
                    logger.debug("Cancel exeption")
            await asyncio.sleep(10)

    async def start(self):
        await asyncio.gather(self.check_config_file())

# Sử dụng
task_manager = TaskManager()
asyncio.run(task_manager.start())