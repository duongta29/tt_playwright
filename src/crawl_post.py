import asyncio
from playwright.async_api import async_playwright
from utils.logger import logger
import config.config as cf
import time
import captcha.captcha as solve_captcha
from kafka import KafkaProducer
from process_data import *
import pickle
from post_tiktok_etractor import PostTikTokExtractor, PostCommentExtractor, PostReplyExtractor
from api_check_post import insert

### GLOBAL ###
producer = KafkaProducer(bootstrap_servers=[cf.kafa_address])


### DEFINE ###
async def handle_response(response, list_comments, list_replies):
    async def get_response_body():
        if "comment/list/?WebIdLastTime" in response.url:
            try:
                # response = await request.response()
                body = await response.json()
                # print(body)
            except Exception as e:
                print(e)
            list_comment = body["comments"]
            if list_comment is not None:
                for comment in list_comment:
                    list_comments.append(comment)
        if "comment/list/reply/?WebIdLastTime" in response.url:
            try:
                body = await response.json()
                # print(body)
            except Exception as e:
                print(e)
            list_reply = body["comments"]
            if list_reply is not None:
                for reply in list_reply:
                    list_replies.append(reply)  
    await get_response_body()

async def get_infor_text(page, source_id, link):
        async with async_playwright() as p:
            try:
                element_infor_text = await page.query_selector('#__UNIVERSAL_DATA_FOR_REHYDRATION__')
                # Lấy thuộc tính "text" của phần tử
                if element_infor_text:
                    infor_text = await page.evaluate('(element) => element.textContent', element_infor_text)
                    infor_text = json.loads(infor_text)
                    infor_text = infor_text["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]
                    return infor_text
                else: 
                    element_infor_text = await page.query_selector('#SIGI_STATE')
                    if element_infor_text:
                        infor_text = await page.evaluate('(element) => element.textContent', element_infor_text)
                        infor_text = json.loads(infor_text)
                        infor_text = infor_text["ItemModule"][source_id]
                        return infor_text
                    else:
                        raise Exception("Element not found")
            except Exception as e:
                print(f"Can't crawl {link} due to Exception: {e}")
                
async def scroll_comment(page = None):
    async with async_playwright() as p:
        cmts = []
        check = 1
        while (len(cmts) != check):
            check = len(cmts)
            cmts = []
            await page.mouse.wheel(0,3000)
            try: 
                cmts = await page.query_selector_all('.css-1i7ohvi-DivCommentItemContainer')
            except Exception as e:
                print(e)
            time.sleep(2)
        try:
            await page.evaluate('window.scrollTo(0, 0)')
        except:
                pass
        for cmt in cmts:
            BOOL = True
            while(BOOL):
                reply_element = await cmt.query_selector('xpath=//p[contains(@data-e2e, "view-more-")]')
                if reply_element is not None:
                    await reply_element.click()
                    await page.mouse.wheel(0,200)
                    await asyncio.sleep(1)
                else:
                    BOOL = False

async def crawl_comment(page = None, list_comments=list, list_replies= list):
    comments = []
    async with async_playwright() as p:
        for comment_dict in list_comments:
            comment_extractor: PostCommentExtractor = PostCommentExtractor(page = page, comment_dict = comment_dict)
            comment = comment_extractor.extract()
            del comment_extractor
            comments.append(comment)
            write_post_to_file(post=comment)
            try: 
                if comment_dict["reply_comment"] is not None:
                    list_reply = comment_dict["reply_comment"]
                    for reply_dict in list_reply:
                        reply_extractor: PostReplyExtractor = PostReplyExtractor(page = page, reply_dict = reply_dict) 
                        reply = reply_extractor.extract()
                        del reply_extractor
                        comments.append(reply)
                        write_post_to_file(post=reply)
            except Exception as e:
                 logger.error(f"Error to crawl comment with Exception {e}")
        for reply_dict in list_replies:
            reply_extractor: PostReplyExtractor = PostReplyExtractor(page = page, reply_dict = reply_dict) 
            reply = reply_extractor.extract()
            del reply_extractor
            comments.append(reply)
            write_post_to_file(post = reply)
        return comments
    
async def push_kafka(posts, comments, mode):
    async with async_playwright() as p:
        if mode == 5:
            topic = "osint-posts-update"
        else:
            topic = "osint-posts-raw"
        if len(posts) > 0:
            bytes_obj = pickle.dumps([ob.__dict__ for ob in posts])
            producer.send(topic, bytes_obj)
            producer.flush()
            if len(comments) > 0:
                bytes_obj = pickle.dumps([ob.__dict__ for ob in comments])
                producer.send(topic, bytes_obj)
                producer.flush()
            logger.debug(f"Done push {topic}")
            return 1
        else:
            logger.warning(f"Error to push {topic} because no post to push")
            return 0
        

async def crawl_post(page , link_post , mode ):
    async with async_playwright() as p:
        try:
            page_name = link_post.split('@')[1].split('/')[0]
            source_id = link_post.split('/')[-1]
            start = time.time()
            list_comments = []
            list_replies =[]
            # page.route("**", lambda route: await route.continue_())
            posts = []
            page.on("response", lambda response: handle_response(response, list_comments, list_replies))
            await page.goto(link_post)
            await page.mouse.wheel(0,500)
            time.sleep(5)
            await solve_captcha.check_captcha(page = page)
            logger.debug(f" >>> Crawling: {link_post} ...")
            infor_text = await get_infor_text(page, source_id = source_id, link = link_post)
            post_extractor: PostTikTokExtractor = PostTikTokExtractor(page = page, link=link_post, source_id=source_id, infor_text = infor_text)
            post = post_extractor.extract()
            posts.append(post)
            await scroll_comment(page=page)
            if post is not None:
                write_post_to_file(post=post)
                comments = await crawl_comment(page, list_comments=list_comments, list_replies=list_replies)
                try:
                    push_kafka_post = await push_kafka(posts= posts, comments= comments, mode = mode)
                except:
                    logger.error(f"Error to push kafka Exception")
            if mode != 5:
                try: 
                    update_file_crawled(page_name=page_name, video_id=source_id)
                except:
                    logger.warning("Cant insert link to local database")
                try:
                    insert_post = insert(table_name="tiktok_video",object_id=page_name, links=source_id) 
                except:
                    logger.warning("Cant insert link to api")
                end = time.time()
                logger.debug(f"Done crawl {link_post} in {end-start}s")
        except Exception as e:
            logger.error(f"Cant crawl post by {e}")
        
        

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await context.tracing.start(screenshots = True, snapshots = True, sources = True)
        page = await context.new_page()
        page_size = {"width": 1280, "height": 720}
        await page.set_viewport_size(page_size)
        await page.goto("https://www.tiktok.com/")
        cookie = "tt_csrf_token=nUhyd6nK-SpOPJf18UdlR1YSMNxldPglQOvE; tt_chain_token=63qdQtS+RXBQnh9XOBZ5BQ==; perf_feed_cache={%22expireTimestamp%22:1703646000000%2C%22itemIds%22:[%227300196461411699974%22%2C%227288797089809665285%22]}; tiktok_webapp_theme=light; passport_fe_beating_status=false; s_v_web_id= verify_lqkdjklr_s6QR8g5s_wy2v_4VlM_Bz25_aYVmGNHmUBQn; passport_csrf_token_default=dd5fdda537431e4fc2efce5c8d2b55d2; passport_csrf_token=dd5fdda537431e4fc2efce5c8d2b55d2; multi_sids=dd5fdda537431e4fc2efce5c8d2b55d2; cmpl_token=AgQQAPOFF-RO0rT2K46M4d0__-ljSWZP_4AOYNKvlQ; passport_auth_status=None; passport_auth_status_ss=None; sid_guard=59ea4699d5b69dfaec2347c2be4a3679%7C1703475902%7C15552000%7CSat%2C+22-Jun-2024+03%3A45%3A02+GMT; uid_tt=a7f163ea828aa38afce7b7324403a4adeb867c2a32cc4e8b4f3758eed512a48b; uid_tt_ss=a7f163ea828aa38afce7b7324403a4adeb867c2a32cc4e8b4f3758eed512a48b; sid_tt=59ea4699d5b69dfaec2347c2be4a3679; sessionid=59ea4699d5b69dfaec2347c2be4a3679; sessionid_ss=59ea4699d5b69dfaec2347c2be4a3679; sid_ucp_v1=1.0.0-KDA4YjFlMjllYzQ0NTZiODA5YTFjM2JmZWVlZGI2NWEyNjY2ZDgzNTgKIAiGiMymkKWx5GQQvvWjrAYYswsgDDDLiqOmBjgEQOoHEAMaBm1hbGl2YSIgNTllYTQ2OTlkNWI2OWRmYWVjMjM0N2MyYmU0YTM2Nzk; ssid_ucp_v1=1.0.0-KDA4YjFlMjllYzQ0NTZiODA5YTFjM2JmZWVlZGI2NWEyNjY2ZDgzNTgKIAiGiMymkKWx5GQQvvWjrAYYswsgDDDLiqOmBjgEQOoHEAMaBm1hbGl2YSIgNTllYTQ2OTlkNWI2OWRmYWVjMjM0N2MyYmU0YTM2Nzk; store-idc=alisg; store-country-code=vn; store-country-code-src=uid; tt-target-idc=alisg; tt-target-idc-sign=A5XHEGsOvjU5cryfBt7HXmS_t4xEJ7FQDcWxT7MfLCVR05LWrhyBBZTEeSuiYph9ftCCg-RNneGjPlJaU_qKgl06Su94agDxKYgIBC5wy9eXq5BzJa2IZG_xTaXcarhJ0JTVGXcHAw0MqTLlzjxoRAV-sNtYz9qy3MjUH4HqG2AgrmGW0OR5ByviGqyFNAK_P6-v26vif0VT93IXYSk4iZUGZML-hUnxEly3FHjjsb023bacAvqwqmjzOOhBq3INi8WjK-HFqKqLsGu2NvzU-CY0tpwI0RSPEI5nH5quVNqfuF4rTxS2LbsqtnvMH0kN9U1Wti-NWvkUxZmujMcv1Q-ODt-sXohQJ1tgRShi2wIDpvXkufDf9MTnoGpPtHNkRxNSa9DZkUFMeitEfHW84swUTQVuwL3G1D05kZMdmGNiaSldZwxXFNn-0Z-_ppgoX2C1ew1tTMsnIkrKm6dXQJOSjyhXh4Z9SUZnZ0XWLTLAzIc51xyL9U0uU4aA1GTa; odin_tt=ef90456efe2401a17a077fc217691791ed47c1d8689a02f4f324d8a65a05f21537684ab60475cd4bae7ef010736e5527339cf17e757a0a2aa82590efc76efbe56316247eea2c0464402c621cc840736a; ttwid=1%7CbjLexk1e2U1IglGjy4h4asd59ZVignYfPVHvmq_VbBU%7C1703475854%7C00df7f4b141249fe79470b6856c08f281d983d08f094bff9c14a756ab5ee3a4e; msToken=LkY3hXKQ4we4yTyGj0vGTMp85wGWpa7JBz_Ag8smkIt0WhSJxB_FtcqjAx-Cbu4SjKcncJEqMtVjuUh1jufcHlHCMNbdIRVkUbJ_2s3fuIPk9N1zDIMobFD4Ar6re77om1o=; passport_fe_beating_status=false"
        script = 'javascript:void(function(){ function setCookie(t) { var list = t.split("; "); console.log(list); for (var i = list.length - 1; i >= 0; i--) { var cname = list[i].split("=")[0]; var cvalue = list[i].split("=")[1]; var d = new Date(); d.setTime(d.getTime() + (7*24*60*60*1000)); var expires = ";domain=.tiktok.com;expires="+ d.toUTCString(); document.cookie = cname + "=" + cvalue + "; " + expires; } } function hex2a(hex) { var str = ""; for (var i = 0; i < hex.length; i += 2) { var v = parseInt(hex.substr(i, 2), 16); if (v) str += String.fromCharCode(v); } return str; } setCookie("' + cookie + '"); location.href = "https://tiktok.com"; })();'
        await page.evaluate(script)
        link_post = "https://www.tiktok.com/@vtv24news/video/7336906233753947400"
        await crawl_post(page = page, link_post = link_post)
        time.sleep(2)
        
if __name__ == "__main__":
    asyncio.run(main())
        
    
            