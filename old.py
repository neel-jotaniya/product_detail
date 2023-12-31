import re
import os
import time
import pandas as pd
import requests
import pyautogui
from pdf import merge, remove_all_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

global product_count
product_count = 0
all_data = []
driver = None

def create_driver():
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    return driver

def setup():
    if not os.path.exists("pdfs"):
        os.makedirs("pdfs")
    if not os.path.exists("temp"):
        os.makedirs("temp")

def get_page_num(data):
    matches = re.findall(r'\b\d+\b', data)
    last_match = matches[-1]
    print(last_match)
    return int(last_match)
    
def download_pdf(i):
    button = driver.find_element(By.XPATH, '//*[@id="viewer"]/div[2]/div/button[2]')
    button.click()
    time.sleep(6)
    cwd = os.getcwd()
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.typewrite(f"{cwd}\\temp\\temp{i}", interval=0.1)
    time.sleep(1)
    pyautogui.press('enter')
    pyautogui.press('enter')
    time.sleep(5)

def scrape_pdf(url, data):
    remove_all_file()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pdf_name_tag = soup.find('h5', class_='viewer__title')
    pdf_name = ''.join(pdf_name_tag.find_all(text=True, recursive=False))
    pdf_name = pdf_name.replace(" ", "")
    page_no_tag = soup.find('div', {'class':'viewer-toolbar__slider'})
    page_no_tag = page_no_tag.find('div')
    total_page = get_page_num(page_no_tag.text)
    print("total_page:", total_page)
    faq = dict()
    questions_div = soup.find_all('div', attrs={'class':'faq__row'})
    for q in questions_div:
        question = q.find('h4').text
        answer = q.find('div').text
        faq[question] = answer
    data['pdf_name'] = pdf_name
    data['FAQ'] = faq
    download_pdf(0)
    for i in range(1,total_page):
        driver.get(f"{url}?p={i+1}")
        download_pdf(i)
    merge(name=pdf_name)
    
def scrape_info(url, data):
    description = ['Brand', 'Model', 'Product', 'Language', 'Filetype']
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    tables = soup.find_all('div', attrs={'class': 'card mb-2'})
    for i in range(len(tables)):
        rows = tables[i].find_all("tr")
        for j in range(len(rows)):
            info = rows[j].find_all('td')
            if i == 0:
                if len(rows) == 6 and j == 3:
                    key = 'EAN'
                elif len(rows) == 6 and j > 3:
                    key = description[j-1]
                else:
                    key = description[j]
            else:
                key = info[0].text
            value = info[1].text
            data[key] = value

def main(url):
    response = requests.get(url)
    all_data = []
    setup()
    global driver
    driver = create_driver()
    if response.status_code != 200: 
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    pagination = soup.find('ul', attrs={'class':'pagination'})
    li = pagination.find_all('li')
    link = li[-1].find('a').get('href')
    total_page = int(link.split("=")[1])
    i = 1
    while i != total_page:
        response = requests.get(f"https://www.manua.ls/?p={i}")
        soup = BeautifulSoup(response.content, 'html.parser')
        products = soup.find_all('div', attrs={'class': 'product-listing__item d-flex justify-content-between align-items-center pl-0'})
        for product in products:
            product_url = product.find('a').get('href')
            print("https://www.manua.ls" + product_url)
            data = dict()
            scrape_info("https://www.manua.ls" + product_url.replace("manual", "specifications"), data) #scrape information
            # scrape_FAQ("https://www.manua.ls"+product_url, data)  #scrape FAQs
            scrape_pdf("https://www.manua.ls"+product_url, data)
            print(data)
            all_data.append(data)
            df = pd.DataFrame(all_data)
            df.to_csv('data.csv', index=False)
        i += 1
# main('https://www.manua.ls/')

def run(url):
    setup()
    global driver
    driver = create_driver()
    main_url = url
    main(main_url) #scrape only five product
    driver.quit()

run('https://www.manua.ls/') # run function can scrape all detali from all product that available at given url

