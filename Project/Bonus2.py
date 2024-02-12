from bs4 import BeautifulSoup
from time import sleep
import urllib3
import json
import pandas as pd
from tqdm import tqdm 

headers = [
    {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,fa;q=0.8',
        'Cookie': 'tracker_glob_new=fuxh0u6; _ga=GA1.1.1110305624.1700733532; tracker_session=2TWrpQn; _sp_ses.13cb=*; TS01c77ebf=010231059174b099361fc81358934f6ee0c53821e18211eb649170bd3eff70476a1e316963ac2f16aedd122f4f73f30137eb459c563177599d752dd44fa425c3ee712e0554b82ac6d92de22be9a5840a7e5501eb0c; _hp2_ses_props.1726062826=%7B%22r%22%3A%22https%3A%2F%2Fwww.digikala.com%2F%22%2C%22ts%22%3A1700921585300%2C%22d%22%3A%22www.digikala.com%22%2C%22h%22%3A%22%2Fsearch%2Fcategory-men-polo-shirt%2F%22%7D; _hp2_id.1726062826=%7B%22userId%22%3A%225696216287148220%22%2C%22pageviewId%22%3A%227745448019084829%22%2C%22sessionId%22%3A%228064032131825496%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; _ga_QQKVTD5TG8=GS1.1.1700908592.4.1.1700921601.0.0.0; _sp_id.13cb=0874ab0f-1994-47aa-9ee4-2d26e42241ac.1700733530.4.1700921603.1700742668.b8f0050e-bf1a-42bb-8465-c823fb1b3507.ebce8a5b-7264-43e8-b75e-2659a07d7b12.dd932bfa-63e0-43e6-85d6-069397bf363b.1700908592373.200',
        'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
    ]


def getHeaders():
    return headers[0]



def get_products_id():
    global number_of_pages, All_IDS, url
    try:
        for i in range(1,number_of_pages+1):
            response = urllib3.request("Get", url.format(i), headers=getHeaders())
            data = BeautifulSoup(response.data, features="html.parser")
            data = json.loads(str(data))
            if data["status"] == 200:
                for pr in data['data']['products']:
                    id = pr["id"]
                    All_IDS.append(id)
            else:
                print("PAGE_LEECH_ERROR", data["status"], data['message'])
                sleep(0.3)
                response = urllib3.request("Get", url.format(i), headers=getHeaders())
                data = BeautifulSoup(response.data, features="html.parser")
                data = json.loads(str(data))
                if data["status"] == 200:
                    for pr in data['data']['products']:
                        id = pr["id"]
                        All_IDS.append(id)
        print("ALL PRODUCTS_ID LEECHED")
        print("Num Products:", len(All_IDS))
    except Exception as e:
        print("ERROR in get_products_id. Page:", i,"ERROR:",e)
        sleep(0.3)
        get_products_id()


def get_product_info(id):
    global leeched, all_info
    try:
        pr_res = urllib3.request("Get", f"https://api.digikala.com/v2/product/{id}/", headers=getHeaders())
        pr_data = BeautifulSoup(pr_res.data,features="html.parser")
        data = json.loads(str(pr_data))
        if(data['status']==200):
            title_fa = data['data']['product']['title_fa']
            title_en = data['data']['product']['title_en']
            image_url = data['data']['product']['images']['main']['url'][0]
            brand = data['data']['product']['data_layer']['brand']
            category = data['data']['product']['data_layer']['category']
            price = data['data']['product']['default_variant']['price']['selling_price']
            shipment_methods = data['data']['product']['default_variant']['shipment_methods']['description']
            cpu = data['data']['product']['review']['attributes'][0]['values'][0]
            ram = data['data']['product']['review']['attributes'][1]['values'][0]
            gpu = data['data']['product']['review']['attributes'][3]['values'][0]
            storage = data['data']['product']['review']['attributes'][2]['values'][0]
            resolution = data['data']['product']['review']['attributes'][4]['values'][0]
            weight = data['data']['product']['specifications'][0]['attributes'][0]['values'][0]
            size = data['data']['product']['specifications'][0]['attributes'][1]['values'][0]
            screen_size = data['data']['product']['specifications'][0]['attributes'][18]['values'][0]
            included_items = data['data']['product']['specifications'][0]['attributes'][-1]['values'][0]
            last_comments = data['data']['product']['last_comments'][0]['body']
            all_info.loc[len(all_info)] = [id, title_fa, title_en, image_url, brand, category, price, shipment_methods, cpu, ram, gpu, storage, resolution, weight, size, screen_size, included_items, last_comments]
            leeched+=1
        else:
            print("LEECH_Error_Info:",data['status'], id)
            sleep(0.1)
    except Exception as e:
        print(f"ERROR in get_product_info {id}:",e)
        sleep(0.3)



def get_pages_info(url):
    global number_of_pages
    try:
        response = urllib3.request("Get", url.format(1), headers=getHeaders())
        data = BeautifulSoup(response.data, features="html.parser")
        data = json.loads(str(data))
        if data["status"] == 200:
            number_of_pages = data['data']['pager']['total_pages']
            print("Pages:", data['data']['pager']['total_pages'], "Products:", data['data']['pager']['total_items'])
            if(number_of_pages>100):
                print("pages are more than 100. we will only leech first 100.")
                number_of_pages = 100
    except Exception as e:
        print("get_pages_info Error:", e)

All_IDS = []
number_of_pages = 100



url = "https://api.digikala.com/v1/categories/notebook-netbook-ultrabook/search/?seo_url=&page={0}"

leeched = 0
# f = open("LOGS.txt",'a')

print("Getting Pages Info")
get_pages_info(url)
number_of_pages = 10
get_products_id()



all_info = pd.DataFrame(columns=['id', 'title_fa', 'title_en', 'image_url', 'brand', 'category', 'price', 'shipment_methods', 'cpu', 'ram', 'gpu', 'storage', 'resolution', 'weight', 'size', 'screen_size', 'included_items', 'last_comment'])
print("Starting Loop")

for id in tqdm(All_IDS):
    get_product_info(id)

print("Finished")
print("Total Leeched:", leeched)
all_info.to_csv("DATA.csv", encoding="utf-8-sig")