import config.config as cf
import requests
from utils.logger import logger


api_address=cf.api_address

def get_links(table_name, object_id):
    url = f"{api_address}/get-links/{table_name}/{object_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")

# API insert link đã crawl vào db
def insert(table_name, object_id, links):
    if api_address == "":
        logger.warning("Cant insert api because dont have api address")
    else:
        if isinstance(links, list):
            links = ",".join(links)
        url = f"{api_address}/insert/{table_name}/{object_id}?new_links={links}"
        try:
            response = requests.post(url)
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {str(e)}")