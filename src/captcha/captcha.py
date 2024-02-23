import cv2
import requests
import time
# from login import TiktokLogin
import asyncio
import captcha.circle as circle
from playwright.async_api import async_playwright
from utils.logger import logger



new_width = 340
new_height = 212
### CLASS ###
class Rotate:
    def __init__(self, page, page_size = {"width": 0, "height": 0}):
        self.page = page
        self.page_size = page_size
        
    async def getLink(self):
        async with async_playwright() as p:
            try:
                outer_element = self.page.get_by_test_id("whirl-outer-img")
                outer_img = await outer_element.get_attribute("src")
                inner_element = self.page.get_by_test_id("whirl-inner-img")
                inner_img = await inner_element.get_attribute("src")
                outer = 'src/captcha/outer.jpg'
                inner = 'src/captcha/inner.jpg'
                response = requests.get(outer_img)
                with open(outer, 'wb') as file:
                    file.write(response.content)
                time.sleep(1)
                response = requests.get(inner_img)
                with open(inner, 'wb') as file:
                    file.write(response.content)
                time.sleep(1)
            except:
                refresh_button = await self.page.query_selector('#secsdk_captcha_refresh--icon')
                refresh_button.click()
                time.sleep(2)
                return await self.getLink()
        
    async def rotateMatches(self):
        async with async_playwright() as p:
            await self.getLink()
            angle = circle.single_discern("src/captcha/inner.jpg","src/captcha/outer.jpg","src/captcha/result.png")
            px = (271 * angle) / 360
            return px
    
    async def slider(self):
        async with async_playwright() as p:
            c = 0
            while(c == 0):
                # time.sleep(1.5)
                try:
                    button = await self.page.query_selector('.secsdk-captcha-drag-icon')
                    pixels = await self.rotateMatches()
                    logger.debug("Slider to solve rotate captcha")
                    await button.hover()
                    await self.page.mouse.down()
                    current_position = (self.page_size["width"]/2) - (340/2) + (64.5/2)
                    step = 25
                    total = 0
                    while total < pixels:
                        if pixels - total < step:
                            step = pixels - total
                        # Di chuyển chuột theo offset
                        await self.page.mouse.move(x = current_position + step,y = 0, steps= 1)
                        current_position += step
                        await asyncio.sleep(0.1)
                        total += step
                    await asyncio.sleep(0.5)
                # Kích hoạt thao tác "click" trên button
                    await self.page.mouse.up()
                    time.sleep(3)
                except Exception as e:
                    c = 1
                    logger.debug("Solvered")
                    break
             
    async def rotateSolver(self):
        async with async_playwright() as p:
            logger.debug("Solver captcha")
            return await self.slider()
        
    async def check_captcha(self):
        async with async_playwright() as p:
            try:
                print("Check Captcha")
                outer_element = self.page.get_by_test_id("whirl-outer-img")
                outer_img = await outer_element.get_attribute("src")
                print("Solver captcha rortate")
                return await self.rotateSolver()
            except:
                logger.debug("No captcha")
                
class Puzzle:
    def __init__(self, page, page_size = {"width": 0, "height": 0}):
        self.page = page
        self.page_size = page_size
        
    async def getLink(self):
        async with async_playwright() as p:
            try:
                puzzle_element = await self.page.query_selector('#captcha-verify-image')
                puzzle_img = await puzzle_element.get_attribute("src")
                piece_element = await self.page.query_selector('.captcha_verify_img_slide')
                piece_img = await piece_element.get_attribute("src")
                puzzle = 'src\captcha\puzzle.jpg'
                piece = 'src\captcha\piece.jpg'
                response = requests.get(puzzle_img)
                with open(puzzle, 'wb') as file:
                    file.write(response.content)
                response = requests.get(piece_img)
                with open(piece, 'wb') as file:
                    file.write(response.content)
                time.sleep(2)
            except:
                refresh_button = await self.page.query_selector('#secsdk_captcha_refresh--icon')
                refresh_button.click()
                time.sleep(2)
                return await self.getLink()
        
    async def puzzleMatches(self):
        async with async_playwright() as p:
            await self.getLink()
            img_rgb = cv2.imread('src\captcha\puzzle.jpg')
            img_rgb = cv2.resize(img_rgb, (new_width, new_height))
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            template = cv2.imread('src\captcha\piece.jpg',0)
            template = cv2.resize(template, (68, 68))
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            time.sleep(2)
            return min_loc[0]
    
    async def slider(self):
        async with async_playwright() as p:
            c = 0
            while(c == 0):
                time.sleep(1.5)
                try:
                    button = await self.page.query_selector('.secsdk-captcha-drag-icon')
                    pixels = await self.puzzleMatches()
                    print("Slider to solve puzzle captcha")
                    await button.hover()
                    current_position = (self.page_size["width"]/2) - (340/2) + (64.5/2)
                    await self.page.mouse.down()
                    total = 0
                    step = 25
                    while total < pixels:
                        if pixels - total < step:
                            step = pixels - total
                        # Di chuyển chuột theo offset
                        await self.page.mouse.move(x = current_position + step,y = 0, steps= 1)
                        current_position += step
                        await asyncio.sleep(0.1)
                        total += step
                    await asyncio.sleep(0.5)
                    # Kích hoạt thao tác "click" trên button
                    await self.page.mouse.up()
                except Exception as e:
                    c = 1
                    print("Solvered")
                    break
             
    async def puzzleSolver(self):
        async with async_playwright() as p:
            print("Solver captcha")
            return await self.slider()
        
async def check_captcha(page, page_size= {"width": 1280, "height": 720} ):
    async with async_playwright() as p:
        logger.debug("Check captcha")
        await asyncio.sleep(2)
        captcha_slider = await page.query_selector('.secsdk-captcha-drag-icon')
        if captcha_slider:
            puzzle_element = await page.query_selector('#captcha-verify-image')
            if puzzle_element is not None:
                logger.debug("Solver captcha PUZZLE")
                puzzle = Puzzle(page, page_size=page_size)  # Await the __init__ method
                return await puzzle.puzzleSolver()  # Await the puzzleSolver method
            else:
                # try:
                #     outer_element = page.get_by_test_id("whirl-outer-img")
                #     outer_img = await outer_element.get_attribute("src")
                #     # outer_img = await outer_element.get_attribute("src")
                print("Solver captcha ROTATE")
                rotate = Rotate(page, page_size=page_size)
                return await rotate.rotateSolver()
                # except Exception as e:
                #     logger.debug(e)
        else:
            logger.debug("No captcha")
        
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await context.tracing.start(screenshots = True, snapshots = True, sources = True)
        page = await context.new_page()
        page_size = {"width": 1280, "height": 720}
        await page.set_viewport_size(page_size)
        await page.goto("https://www.tiktok.com/")
        # cookie = "tt_csrf_token=nUhyd6nK-SpOPJf18UdlR1YSMNxldPglQOvE; tt_chain_token=63qdQtS+RXBQnh9XOBZ5BQ==; perf_feed_cache={%22expireTimestamp%22:1703646000000%2C%22itemIds%22:[%227300196461411699974%22%2C%227288797089809665285%22]}; tiktok_webapp_theme=light; passport_fe_beating_status=false; s_v_web_id= verify_lqkdjklr_s6QR8g5s_wy2v_4VlM_Bz25_aYVmGNHmUBQn; passport_csrf_token_default=dd5fdda537431e4fc2efce5c8d2b55d2; passport_csrf_token=dd5fdda537431e4fc2efce5c8d2b55d2; multi_sids=dd5fdda537431e4fc2efce5c8d2b55d2; cmpl_token=AgQQAPOFF-RO0rT2K46M4d0__-ljSWZP_4AOYNKvlQ; passport_auth_status=None; passport_auth_status_ss=None; sid_guard=59ea4699d5b69dfaec2347c2be4a3679%7C1703475902%7C15552000%7CSat%2C+22-Jun-2024+03%3A45%3A02+GMT; uid_tt=a7f163ea828aa38afce7b7324403a4adeb867c2a32cc4e8b4f3758eed512a48b; uid_tt_ss=a7f163ea828aa38afce7b7324403a4adeb867c2a32cc4e8b4f3758eed512a48b; sid_tt=59ea4699d5b69dfaec2347c2be4a3679; sessionid=59ea4699d5b69dfaec2347c2be4a3679; sessionid_ss=59ea4699d5b69dfaec2347c2be4a3679; sid_ucp_v1=1.0.0-KDA4YjFlMjllYzQ0NTZiODA5YTFjM2JmZWVlZGI2NWEyNjY2ZDgzNTgKIAiGiMymkKWx5GQQvvWjrAYYswsgDDDLiqOmBjgEQOoHEAMaBm1hbGl2YSIgNTllYTQ2OTlkNWI2OWRmYWVjMjM0N2MyYmU0YTM2Nzk; ssid_ucp_v1=1.0.0-KDA4YjFlMjllYzQ0NTZiODA5YTFjM2JmZWVlZGI2NWEyNjY2ZDgzNTgKIAiGiMymkKWx5GQQvvWjrAYYswsgDDDLiqOmBjgEQOoHEAMaBm1hbGl2YSIgNTllYTQ2OTlkNWI2OWRmYWVjMjM0N2MyYmU0YTM2Nzk; store-idc=alisg; store-country-code=vn; store-country-code-src=uid; tt-target-idc=alisg; tt-target-idc-sign=A5XHEGsOvjU5cryfBt7HXmS_t4xEJ7FQDcWxT7MfLCVR05LWrhyBBZTEeSuiYph9ftCCg-RNneGjPlJaU_qKgl06Su94agDxKYgIBC5wy9eXq5BzJa2IZG_xTaXcarhJ0JTVGXcHAw0MqTLlzjxoRAV-sNtYz9qy3MjUH4HqG2AgrmGW0OR5ByviGqyFNAK_P6-v26vif0VT93IXYSk4iZUGZML-hUnxEly3FHjjsb023bacAvqwqmjzOOhBq3INi8WjK-HFqKqLsGu2NvzU-CY0tpwI0RSPEI5nH5quVNqfuF4rTxS2LbsqtnvMH0kN9U1Wti-NWvkUxZmujMcv1Q-ODt-sXohQJ1tgRShi2wIDpvXkufDf9MTnoGpPtHNkRxNSa9DZkUFMeitEfHW84swUTQVuwL3G1D05kZMdmGNiaSldZwxXFNn-0Z-_ppgoX2C1ew1tTMsnIkrKm6dXQJOSjyhXh4Z9SUZnZ0XWLTLAzIc51xyL9U0uU4aA1GTa; odin_tt=ef90456efe2401a17a077fc217691791ed47c1d8689a02f4f324d8a65a05f21537684ab60475cd4bae7ef010736e5527339cf17e757a0a2aa82590efc76efbe56316247eea2c0464402c621cc840736a; ttwid=1%7CbjLexk1e2U1IglGjy4h4asd59ZVignYfPVHvmq_VbBU%7C1703475854%7C00df7f4b141249fe79470b6856c08f281d983d08f094bff9c14a756ab5ee3a4e; msToken=LkY3hXKQ4we4yTyGj0vGTMp85wGWpa7JBz_Ag8smkIt0WhSJxB_FtcqjAx-Cbu4SjKcncJEqMtVjuUh1jufcHlHCMNbdIRVkUbJ_2s3fuIPk9N1zDIMobFD4Ar6re77om1o=; passport_fe_beating_status=false"
        # script = 'javascript:void(function(){ function setCookie(t) { var list = t.split("; "); console.log(list); for (var i = list.length - 1; i >= 0; i--) { var cname = list[i].split("=")[0]; var cvalue = list[i].split("=")[1]; var d = new Date(); d.setTime(d.getTime() + (7*24*60*60*1000)); var expires = ";domain=.tiktok.com;expires="+ d.toUTCString(); document.cookie = cname + "=" + cvalue + "; " + expires; } } function hex2a(hex) { var str = ""; for (var i = 0; i < hex.length; i += 2) { var v = parseInt(hex.substr(i, 2), 16); if (v) str += String.fromCharCode(v); } return str; } setCookie("' + cookie + '"); location.href = "https://tiktok.com"; })();'
        # await page.evaluate(script)
        # Check
        login = page.get_by_text("Use phone / email / username")
        await login.click()
        login_by_username = page.get_by_text("Log in with email or username")
        await login_by_username.click()
        # username = page.get_by_role("input", name= "username")
        await page.get_by_placeholder("Email or username").fill("babysunny2906")
        await page.get_by_placeholder("Password").fill("Ncsduong@29s")
        await page.get_by_role("dialog", name="Log in").get_by_role("button", name="Log in").click()
        # await page.goto('https://www.tiktok.com/search/video?q=chang chang tv&t=1708056567016')
        time.sleep(3)
        await check_captcha(page, page_size=page_size)
        time.sleep(2)
        
    
# # ### EXECUTE ###
if __name__ == "__main__":
    asyncio.run(main())
# main()

