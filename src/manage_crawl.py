from playwright.async_api import async_playwright, Page
from utils.logger import logger
import config.config as cfg
import time
from es import get_link_es
from api_check_post import get_links
from login import *
from datetime import datetime, timedelta
import captcha.captcha as solve_captcha
import os
import schedule
from crawl_post import *
import threading


class SearchUser:
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
            list_link = await self.get_link_list_by_search_user(page = self.page, config=self.config)
            for link in list_link:
                    await crawl_post(page = self.page, link_post = link, mode = 3)
            logger.debug("Sleep in 4 hour")
            await asyncio.sleep(4*60*60)
            return await self.run()
        
    #config mode id == 3 : search user
    async def get_link_list_by_search_user(self, page = Page, config = dict):
        async with async_playwright() as p:
            list_user = config["mode"]["list_page"] 
            # links = []
            list_links = []
            for user in list_user:
                await page.goto(user)
                await page.mouse.wheel(0,200)
                time.sleep(5)
                await solve_captcha.check_captcha(page)
                BOOL = True
                check = 0
                check_list = 1
                list_links_element=[]
                link_checked = []
                while (len(list_links_element) != check_list and BOOL):
                    # links = []
                    check_list = len(list_links_element)
                    await page.mouse.wheel(0,3000)
                    time.sleep(2)
                    list_links_element = await page.query_selector_all('//*[@data-e2e="user-post-item-desc"]')
                    for link in list_links_element:
                        element = await link.query_selector('a')
                        href = await element.get_attribute('href')
                        if href not in link_checked:
                            check_link = check_link_crawled(link = href)
                            if check_link:
                                check += 1
                                link_checked.append(href)
                            else:
                                if href not in list_links:
                                    list_links.append(href)
                                    link_checked.append(href)
                        if check > 4:
                            BOOL = False
                            break
            return list_links
        
        
class SearchPost:
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
            list_link = await self.get_link_list_by_search_post(page = self.page, config=self.config)
            for link in list_link:
                await crawl_post(page = self.page, link_post = link, mode = 4)
            logger.debug("Sleep in 4 hour")
            asyncio.sleep(4*60*60)
            return await self.run()

    #config mode id == 4 : search post
    async def get_link_list_by_search_post(self, page = Page, config = dict):
        async with async_playwright() as p:
            keywords = config["mode"]["keyword"] 
            list_links = []
            for keyword in keywords:
                await page.goto(cf.search_post_tiktok + keyword)
                await page.mouse.wheel(0,500)
                time.sleep(5)
                await solve_captcha.check_captcha(page)
                BOOL = True
                check_list = 1
                link_checked=[]
                while len(list_links) != check_list:
                    check_list = len(list_links)
                    await page.mouse.wheel(0,3000)
                    time.sleep(2)
                    list_links_element = await page.query_selector_all('//*[contains(@class, "DivItemContainerForSearch")]')
                    # asyncio.sleep(2.5)
                for link in list_links_element:
                        element = await link.query_selector('a')
                        href = await element.get_attribute('href')
                        if href not in link_checked:
                            check_link = check_link_crawled(link = href)
                            if check_link:
                                link_checked.append(href)
                            else:
                                if href not in list_links:
                                    list_links.append(href)
                                    link_checked.append(href)
            return list_links
    
class Update:
    def __init__(self) -> None:
        self.config = self.read_config_update()
        self.account = self.config["account"]
        self.tasks = {}
        self.links_crawling = []
        
    def read_config_update(self):
        with open("config\config_update.json", "r", encoding="utf-8") as config_file:
            config_data = json.load(config_file)
        return config_data
        
  
    async def manage_update(self):
        # links_crawling = []
        while True:
            with open("link_to_update.txt", 'r') as file:
                links_check = [line.strip() for line in file]
            if links_check != self.links_crawling:
                if len(self.tasks) != 0:
                    for task_id in list(set(self.tasks.keys())):
                        task = self.tasks.pop(task_id)
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            logger.debug("Cancel exeption")
                        except Exception as e:
                            print(e)
                new_task = asyncio.create_task(self.update_post())
                self.links_crawling = links_check
                self.tasks["new task"] = new_task
            await asyncio.sleep(60)
                
    async def run(self):
        logger.info("Run update")
        # try:
        schedule_thread = threading.Thread(target=self.schedule)
        schedule_thread.start()
        await asyncio.gather(self.manage_update())


    #config mode id == 5 : update
    def get_link_list_es(self):
        range_date = self.config["mode"]["range_date"]
        format_str = "%m/%d/%Y %H:%M:%S"
        now = datetime.now()
        link_to_update = []
        for range_value in range_date:
            gte = now - timedelta(days=int(range_value))
            lte = now - timedelta(days=int(range_value)-1)
            gte = gte.replace(hour=0, minute=0, second=0, microsecond=0)
            lte = lte.replace(hour=0, minute=0, second=0, microsecond=0)
            gte_str = gte.strftime(format_str)
            lte_str = lte.strftime(format_str)
            logger.debug("Get link es")
            link = get_link_es(gte=gte_str, lte=lte_str)
            link_to_update.extend(link)
        with open("link_to_update.txt", "w") as file:
            for item in link_to_update:
                file.write(str(item) + "\n")
                
    def schedule(self):
        start_time_run = self.config["mode"]["start_time_run"]
        schedule.every().day.at(start_time_run).do(self.get_link_list_es)
        while True:
            schedule.run_pending()
            time.sleep(1)
                
    async def update_post(self):
        async with async_playwright() as p:
            # arguments = self.config["listArgumentChromium"]
            # browser = await p.chromium.launch(headless=False, args=arguments)
            try:
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
                link_done = list()
                with open("src/link_to_update.txt", 'r') as file:
                    links = [line.strip() for line in file]
                if links:
                    for link in links:
                        await crawl_post(page=self.page, link_post=link, mode=5)
            except Exception as e:
                print(e)
                
                

def check_link_crawled(link):
    page_name = link.split('@')[1].split('/')[0]
    video_id = link.split('/')[-1]
    try:
        data_crawled = get_links(table_name="tiktok_video", object_id= page_name)
        if "links" in data_crawled:
            if video_id in data_crawled["links"]:
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        logger.error("Cant check link in api")
        folder_path = "data crawled"
        # Kiểm tra xem file có tên trùng với page_name tồn tại trong thư mục hay không
        file_path = os.path.join(folder_path, f"{page_name}.txt")
        if not os.path.exists(file_path):
            return False
        # Đọc nội dung của file
        with open(file_path, "r") as file:
            content = file.read().splitlines()
        # Kiểm tra xem video_id có trùng với phần tử nào trong nội dung hay không
        if video_id in content:
            return True
        return False