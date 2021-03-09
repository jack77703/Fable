from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import openpyxl
from openpyxl import load_workbook
import time
from datetime import datetime
from bs4 import BeautifulSoup
import os
import pandas as pd
from urllib import parse
import requests

# usecols 可避免讀取全量數據，而是以分析需求為導向選擇特定數據，可以大幅提高效率。


fold_path = "/Users/jack/Desktop/Fable/crawler_data"


def crawler():
    chrome_options = Options()  # 啟動無頭模式
    chrome_options.add_argument('--headless')  # 規避google bug
    chrome_options.add_argument('--disable-gpu')
    chrome = webdriver.Chrome(
        executable_path='./chromedriver', chrome_options=chrome_options)

    p = 1
    df = pd.DataFrame()  # 暫存當頁資料，換頁時即整併到dfAll
    dfAll = pd.DataFrame()  # 存放所有資料
    close = 0
    while True:
        if(close == 1):
            chrome.close()
            break
        url = "https://www.gusta.com.tw/products?page=" + str(p)
        print("處理頁面:", url)
        # 如果頁面超過(找不到)，直接印出completed然後break跳出迴圈
        try:
            chrome.get(url)
        except:
            break

        time.sleep(1)

        i = 1
        while(i < 25):
            try:
                title = chrome.find_element_by_xpath(
                    "//li[%i]//div[2]/div/div[1]" % (i,)).text
            except:
                close += 1
                break
            try:
                page_link = chrome.find_element_by_xpath(
                    "//li[%i]/product-item/a" % (i,)).get_attribute('href')
                make_id = parse.urlsplit(page_link)
                page_id = make_id.path
                page_id = page_id.lstrip("/products/")
            except:
                i += 1
                if(i == 25):
                    p += 1
                continue
            try:
                find_href = chrome.find_element_by_xpath(
                    "//li[%i]/product-item/a/div[1]/div" % (i,))
                bg_url = find_href.value_of_css_property('background-image')
                pic_link = bg_url.lstrip('url("').rstrip('")')
            except:
                i += 1
                if(i == 25):
                    p += 1
                continue
            try:
                sale_price = chrome.find_element_by_xpath(
                    "//li[%i]/product-item/a/div[2]/div/div[2]/div[2]" % (i,)).text
                sale_price = sale_price.strip('NT$')
                sale_price = sale_price.split()
                sale_price = sale_price[0]
            except:
                i += 1
                if(i == 25):
                    p += 1
                continue
            try:
                ori_price = chrome.find_element_by_xpath(
                    "//li[%i]/product-item/a/div[2]/div/div[2]/div[1]" % (i,)).text
                if (ori_price == "售完"):
                    i += 1
                    if(i == 25):
                        p += 1
                    continue
                else:
                    ori_price = ori_price.strip('NT$')
                    ori_price = ori_price.split()
                    ori_price = ori_price[0]
            except:
                i += 1
                if(i == 25):
                    p += 1
                continue

            i += 1
            if(i == 25):
                p += 1

            df = pd.DataFrame(
                {
                    "title": [title],
                    "page_link": [page_link],
                    "page_id": [page_id],
                    "pic_link": [pic_link],
                    "ori_price": [ori_price],
                    "sale_price": [sale_price]
                })

            now = datetime.now()
            date_time = now.strftime("%Y%m%d")

            dfAll = pd.concat([dfAll, df])
            dfAll = dfAll.reset_index(drop=True)
            dfAll.to_excel(fold_path + "/2_Legust_"+date_time+".xlsx")


def api():
    now = datetime.now()
    date_time = now.strftime("%Y%m%d")
    headers = {
        'authorization': "Bearer 24sEt76giGrRTLtCR0IRiMTEGagRyqjT3VPnwoA7",
        'cache-control': "no-cache",
    }

    url = "http://layer.d-blueprint.com/api/import/product"
    files = {"file": open(fold_path + "/2_Legust_"+date_time+".xlsx", "rb")}
    response = requests.post(url, files=files, headers=headers)  # 使用post上傳
    print(response.status_code)
    # os.remove(fold_path + "/2_Legust_"+date_time+".xlsx")


def main():
    crawler()
    api()


main()
