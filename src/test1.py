import asyncio
from playwright.async_api import async_playwright, expect, Route
import concurrent.futures
import time
import json
import config.config as cf
import time
from login import *
import captcha.captcha as solve_captcha
import re
response_queue = asyncio.Queue()

# async def handle_route(route):
#     request = route.request
#     if "comment/list/?WebIdLastTime" in request.url:
#         response = await route.fetch()
#         await response_queue.put(response)  # Đẩy phản hồi vào hàng đợi

# async def process_responses():
#     while True:
#         response = await response_queue.get()
#         with open("response.txt", "a") as file:
# #             file.write(response.url + "\n")
#             file.write(response.text + "\n")

# async def handle_route(route, request):
#     print(request.url)
#     if re.search(r"comment", request.url):
#         try:
#             response = await 
#             print(response)
#         except Exception as e:
#             print(e)
#         # Lấy response của request
#         # response = await request.response()
        
#         # Lấy nội dung response
#         # response_text = await response.text()
        
#         # Ghi nội dung response vào file txt
#         # with open("response.txt", "a") as file:
#         #     file.write(response_text)
#         await route.continue_()
        
#         # Lấy nội dung response
        
        
#         # Tiếp tục xử lý request
#         # await route.continue_()
#     else:
#         # Tiếp tục xử lý request bình thường
#         await route.continue_()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await context.tracing.start(screenshots = True, snapshots = True, sources = True)
        page = await context.new_page()
        await page.set_viewport_size({"width": 1280, "height": 720})
        # page.route("**", lambda route: await route.continue_())
        # replies = []
        # page.on("response", lambda response: handle_response(response, replies))
        # await page.route(re.compile(r"comment/list/\?WebIdLastTime"), handle_route)
        # await page.route(re.compile(r"comment"), handle_route)
        # asyncio.create_task(process_responses())
        # page.on("request", handle_request())
        # page.on("response", lambda response: print("<<", response.status, response.url))
        await page.goto("https://www.tiktok.com/")
        # context.wait_for_page(page)
        #Check
        # login = page.get_by_text("Use phone / email / username")
        # await login.click()
        # login_by_username = page.get_by_text("Log in with email or username")
        # await login_by_username.click()
        # # username = page.get_by_role("input", name= "username")
        # await page.get_by_placeholder("Email or username").fill("babysunny2906")
        # await page.get_by_placeholder("Password").fill("Ncsduong@29s")
        # await page.get_by_role("dialog", name="Log in").get_by_role("button", name="Log in").click()
        # # cookie = {'name': 'msToken', 'value': 'iBXFqQX8ytC8qD54UWae9qBdCRNWwyzqhg3nDUchfr9iS7sZ_Hsfye3ZYEiOpIzloLGYEtuUt7bGVxGRSg7JtV4sTtEwFsFQ_IUo6LztsuPUPrfuCNxoNyMsq6SLCA43N_gHA9HYHwbnEIkZ', 'domain': 'www.tiktok.com', 'path': '/', 'expires': 1714624729, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}
        # # await context.add_cookies(cookie)
        # cookies = await context.cookies()
        # with open("cookies.txt", "w") as file:
        #     for cookie in cookies:
        #         file.write(f"{cookie['name']} = {cookie['value']}\n")
        
        # print("Danh sách cookies:")
        # for cookie in cookies:
        #     print(cookie)
        # cookies_file = "cookies.txt"

        # # Đọc danh sách cookies từ tệp tin
        # cookies = []
        # with open(cookies_file, "r") as file:
        #     lines = file.readlines()
        #     for line in lines:
        #         line = line.strip()  # Xóa khoảng trắng và ký tự xuống dòng thừa
        #         if ":" in line:
        #             name, value = line.split(":", 1)
        #             cookie = {"name": name.strip(), "value": value.strip(),"url": "https://www.tiktok.com/explore"}
        #             cookies.append(cookie)
        cookie = "tt_csrf_token=nUhyd6nK-SpOPJf18UdlR1YSMNxldPglQOvE; tt_chain_token=63qdQtS+RXBQnh9XOBZ5BQ==; perf_feed_cache={%22expireTimestamp%22:1703646000000%2C%22itemIds%22:[%227300196461411699974%22%2C%227288797089809665285%22]}; tiktok_webapp_theme=light; passport_fe_beating_status=false; s_v_web_id= verify_lqkdjklr_s6QR8g5s_wy2v_4VlM_Bz25_aYVmGNHmUBQn; passport_csrf_token_default=dd5fdda537431e4fc2efce5c8d2b55d2; passport_csrf_token=dd5fdda537431e4fc2efce5c8d2b55d2; multi_sids=dd5fdda537431e4fc2efce5c8d2b55d2; cmpl_token=AgQQAPOFF-RO0rT2K46M4d0__-ljSWZP_4AOYNKvlQ; passport_auth_status=None; passport_auth_status_ss=None; sid_guard=59ea4699d5b69dfaec2347c2be4a3679%7C1703475902%7C15552000%7CSat%2C+22-Jun-2024+03%3A45%3A02+GMT; uid_tt=a7f163ea828aa38afce7b7324403a4adeb867c2a32cc4e8b4f3758eed512a48b; uid_tt_ss=a7f163ea828aa38afce7b7324403a4adeb867c2a32cc4e8b4f3758eed512a48b; sid_tt=59ea4699d5b69dfaec2347c2be4a3679; sessionid=59ea4699d5b69dfaec2347c2be4a3679; sessionid_ss=59ea4699d5b69dfaec2347c2be4a3679; sid_ucp_v1=1.0.0-KDA4YjFlMjllYzQ0NTZiODA5YTFjM2JmZWVlZGI2NWEyNjY2ZDgzNTgKIAiGiMymkKWx5GQQvvWjrAYYswsgDDDLiqOmBjgEQOoHEAMaBm1hbGl2YSIgNTllYTQ2OTlkNWI2OWRmYWVjMjM0N2MyYmU0YTM2Nzk; ssid_ucp_v1=1.0.0-KDA4YjFlMjllYzQ0NTZiODA5YTFjM2JmZWVlZGI2NWEyNjY2ZDgzNTgKIAiGiMymkKWx5GQQvvWjrAYYswsgDDDLiqOmBjgEQOoHEAMaBm1hbGl2YSIgNTllYTQ2OTlkNWI2OWRmYWVjMjM0N2MyYmU0YTM2Nzk; store-idc=alisg; store-country-code=vn; store-country-code-src=uid; tt-target-idc=alisg; tt-target-idc-sign=A5XHEGsOvjU5cryfBt7HXmS_t4xEJ7FQDcWxT7MfLCVR05LWrhyBBZTEeSuiYph9ftCCg-RNneGjPlJaU_qKgl06Su94agDxKYgIBC5wy9eXq5BzJa2IZG_xTaXcarhJ0JTVGXcHAw0MqTLlzjxoRAV-sNtYz9qy3MjUH4HqG2AgrmGW0OR5ByviGqyFNAK_P6-v26vif0VT93IXYSk4iZUGZML-hUnxEly3FHjjsb023bacAvqwqmjzOOhBq3INi8WjK-HFqKqLsGu2NvzU-CY0tpwI0RSPEI5nH5quVNqfuF4rTxS2LbsqtnvMH0kN9U1Wti-NWvkUxZmujMcv1Q-ODt-sXohQJ1tgRShi2wIDpvXkufDf9MTnoGpPtHNkRxNSa9DZkUFMeitEfHW84swUTQVuwL3G1D05kZMdmGNiaSldZwxXFNn-0Z-_ppgoX2C1ew1tTMsnIkrKm6dXQJOSjyhXh4Z9SUZnZ0XWLTLAzIc51xyL9U0uU4aA1GTa; odin_tt=ef90456efe2401a17a077fc217691791ed47c1d8689a02f4f324d8a65a05f21537684ab60475cd4bae7ef010736e5527339cf17e757a0a2aa82590efc76efbe56316247eea2c0464402c621cc840736a; ttwid=1%7CbjLexk1e2U1IglGjy4h4asd59ZVignYfPVHvmq_VbBU%7C1703475854%7C00df7f4b141249fe79470b6856c08f281d983d08f094bff9c14a756ab5ee3a4e; msToken=LkY3hXKQ4we4yTyGj0vGTMp85wGWpa7JBz_Ag8smkIt0WhSJxB_FtcqjAx-Cbu4SjKcncJEqMtVjuUh1jufcHlHCMNbdIRVkUbJ_2s3fuIPk9N1zDIMobFD4Ar6re77om1o=; passport_fe_beating_status=false"
        script = 'javascript:void(function(){ function setCookie(t) { var list = t.split("; "); console.log(list); for (var i = list.length - 1; i >= 0; i--) { var cname = list[i].split("=")[0]; var cvalue = list[i].split("=")[1]; var d = new Date(); d.setTime(d.getTime() + (7*24*60*60*1000)); var expires = ";domain=.tiktok.com;expires="+ d.toUTCString(); document.cookie = cname + "=" + cvalue + "; " + expires; } } function hex2a(hex) { var str = ""; for (var i = 0; i < hex.length; i += 2) { var v = parseInt(hex.substr(i, 2), 16); if (v) str += String.fromCharCode(v); } return str; } setCookie("' + cookie + '"); location.href = "https://tiktok.com"; })();'
        # browser.execute_script(script)
        await page.evaluate(script)
        # search = page.get_by_placeholder("Search")
        # await search.fill("Nguyễn Phú Trọng")
        # # submit = page.get_by_role("button", name= "submit")
        # # await submit.click()
        # await search.press("Enter")
        # await page.goto("https://www.tiktok.com/search/video?q=chang%20chang%20tv")
        keywords = ["https://www.tiktok.com/@hieuviet55", "https://www.tiktok.com/@_changchang47"]
        links = []
        for keyword in keywords:
            await page.goto(keyword)
            await solve_captcha.check_captcha(page)
            BOOL = True
            check_list = 1
            list_links = []
            while len(list_links) != check_list:
                check_list = len(list_links)
                await page.mouse.wheel(0,3000)
                # asyncio.sleep(3)
                time.sleep(2)
                list_links = await page.query_selector_all('//*[@data-e2e="user-post-item-desc"]')
            for link in list_links:
                element = await link.query_selector('a')
                href = await element.get_attribute('href')
                links.append(href)
        print(links)
        # for reply in replies:
        #     print(reply)
        # for element in elements:
        #     a_element = await element.query_selector('a')
        #     href = await a_element.get_attribute('href')
        #     print(href)
        time.sleep(10)
        
            
        # video = page.get_by_role("tab").filter(has_text=)
        # Thêm cookies vào trình duyệt
        # await context.add_cookies(cookies)
        
        
        
        

        # if element:
            # print("Tìm thấy phần tử:", element)
        # else:
            # print("Không tìm thấy phần tử.")
        # /
        
# def handle_request(request, replies):
#     url = request.url
#     if "comment/list/?WebIdLastTime" in url:
#         response = request.response()
#         print(response)
#         response_body = response.body()
#         content_encoding = response.headers.get("Content-Encoding", "identity")
#         data = sw_decode(response_body, content_encoding)
#         try:
#             data = data.decode("utf8")
#         except:
#             pass
#         data = json.loads(data)
#         list_reply = data["comments"]
#         if list_reply is not None:
#             for reply in list_reply:
#                 replies.append(reply)
                

async def handle_response(response, replies):
    async def get_response_body():
        if "comment/list/?WebIdLastTime" in response.url:
            try:
                # response = await request.response()
                body = await response.json()
                print(body)
                # content_encoding = response.headers.get('Content-Encoding', 'identity')
                # data = sw_decode(response, content_encoding)
                # data = sw_decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
            except Exception as e:
                print(e)
            # response = await request.response()
            # print(response)
            # response_body = response.body
            # content_encoding = response.headers.get("Content-Encoding", "identity")
            # data = sw_decode(response_body, content_encoding)
            # try:
            #     data = data.decode("utf8")
            # except Exception as e:
            #     pass
            # data = json.loads(data)
            list_reply = body["comments"]
            if list_reply is not None:
                for reply in list_reply:
                    replies.append(reply)

    await get_response_body()

# def sw_decode(data, content_encoding):
#     if content_encoding == "gzip":
#         import gzip
#         import io
#         data = gzip.GzipFile(fileobj=io.BytesIO(data)).read()
#     elif content_encoding == "deflate":
#         import zlib
#         data = zlib.decompress(data)
#     return data
    
asyncio.run(main())
        