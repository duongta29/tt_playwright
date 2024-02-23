import asyncio
from playwright.async_api import async_playwright, Page
from utils.logger import logger
import config.config as cf
import time
from login import *
import captcha.captcha as solve_captcha
from config.get_config import *
from manage_crawl import *
from crawl_post import *
import threading

class CrawlManage(object):
    def __init__(self, config) -> None:
        self.config = config
        self.account = config["account"]
        
    async def run(self):
        async with async_playwright() as p:
            # arguments = self.config["listArgumentChromium"]
            # browser = await p.chromium.launch(headless=False, args=arguments)
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            await context.tracing.start(screenshots = True, snapshots = True, sources = True)
            self.page = await context.new_page()
            page_size = {"width": 1280, "height": 720}
            await self.page.set_viewport_size(page_size)
            # self.page = await self.open_chromium()
            await self.page.goto("https://www.tiktok.com/")
            try:
                await login_with_cookies(page= self.page, account=self.account)
            except:
                await get_cookies(page= self.page, account=self.account)
            logger.debug("Done login")
            config_id = self.config["mode"]["id"]
            if config_id == 5:
                logger.debug("Mode update post")
                await self.update(config=self.config)
            else:
                if config_id == 3:
                    logger.debug("Mode search user")
                    list_link = await get_link_list_by_search_user(page = self.page, config=self.config)
                elif config_id == 4:
                    logger.debug("Mode search post")
                    list_link = await get_link_list_by_search_post(page = self.page, config=self.config)
                #crawl post
                for link in list_link:
                    await crawl_post(page = self.page, link_post = link, mode = config_id)
                logger.debug("Sleep in 4 hour")
                asyncio.sleep(4*60*60)
                return await self.run()
    async def update_post(self):
        link_done = list()
        with open("src/link_to_update.txt", 'r') as file:
            links = [line.strip() for line in file]
        if links:
            for link in links:
                await crawl_post(page=self.page, link_post=link, mode=5)
                link_done.append(link)
                if len(link_done) % 10 == 0:
                    result = list(set(links) - set(link_done))
                    break
            with open("src/link_to_update.txt", "w") as file:
                for item in result:
                    file.write(str(item) + "\n")
        # return await self.update_post()
    async def update(self,  config):
        try:
            # Bắt đầu chạy các coroutine
            # task1 = asyncio.create_task(self.update_post())
            # task2 = asyncio.create_task(get_link_list_es( config = config))
            task1 = self.update_post()
            task2 = get_link_list_es( config = config)
            # Chờ cho đến khi cả hai coroutine hoàn thành
            await asyncio.gather(task1,task2)
            return await self.update(config)
        except Exception as e:
            print(e)



           
# async def crawl_manager_task(config):
#     crawler = CrawlManage(config)
#     await crawler.run()     
    
# async def main():
#     tasks = []
#     for config in config_list:
#         task = asyncio.create_task(crawl_manager_task(config))
#         tasks.append(task)

#     await asyncio.gather(*tasks)
    


            
                
            
        
        