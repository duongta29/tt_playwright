import asyncio
from playwright.async_api import async_playwright
from utils.logger import logger
import time
import captcha.captcha as solve_captcha



async def login_with_pass(page = None, account = {}):
    async with async_playwright() as p:
        if page == None:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            await context.tracing.start(screenshots = True, snapshots = True, sources = True)
            page = await context.new_page()
            await page.goto("https://www.tiktok.com/")
        try: 
            login = page.get_by_text("Use phone / email / username")
            await login.click()
            login_by_username = page.get_by_text("Log in with email or username")
            await login_by_username.click()
            # username = page.get_by_role("input", name= "username")
            await page.get_by_placeholder("Email or username").fill(account["username"])
            await page.get_by_placeholder("Password").fill(account["password"])
            await page.get_by_role("dialog", name="Log in").get_by_role("button", name="Log in").click()
            solve_captcha.check_captcha(page=page, page_size = {"width": 1280, "height": 720})
            logger.debug("Login with pass success")
        except Exception as e:
            logger.error(e)
            
async def login_with_cookies(page = None, account = {}):
    async with async_playwright() as p:
        if page == None:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            await context.tracing.start(screenshots = True, snapshots = True, sources = True)
            page = await context.new_page()
            await page.goto("https://www.tiktok.com/")
        try:
            cookie = account["cookies"]
            script = 'javascript:void(function(){ function setCookie(t) { var list = t.split("; "); console.log(list); for (var i = list.length - 1; i >= 0; i--) { var cname = list[i].split("=")[0]; var cvalue = list[i].split("=")[1]; var d = new Date(); d.setTime(d.getTime() + (7*24*60*60*1000)); var expires = ";domain=.tiktok.com;expires="+ d.toUTCString(); document.cookie = cname + "=" + cvalue + "; " + expires; } } function hex2a(hex) { var str = ""; for (var i = 0; i < hex.length; i += 2) { var v = parseInt(hex.substr(i, 2), 16); if (v) str += String.fromCharCode(v); } return str; } setCookie("' + cookie + '"); location.href = "https://tiktok.com"; })();'
            # browser.execute_script(script)
            await page.evaluate(script)
            logger.debug("Login with cookies success")
            time.sleep(2)
        except Exception as e:
            logger.error(e)
            
async def get_cookies(page = None,account = {}):
    async with async_playwright() as p:
        if page == None:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            await context.tracing.start(screenshots = True, snapshots = True, sources = True)
            page = await context.new_page()
            await page.goto("https://www.tiktok.com/")
        try:
            login_with_pass(page=page, account=account)
            cookies = await context.cookies()
            cookies_string = '; '.join([f"{key}={value}" for key, value in cookies.items()])
            with open("cookies.txt", "w") as file:
                file.write(cookies_string)
            logger.debug("Login with cookies success")
        except Exception as e:
            logger.error(e)
        
# asyncio.run(login_with_cookies(account=account))