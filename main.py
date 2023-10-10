import re
import os
import time
import pandas as pd
import requests
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

from bs4 import BeautifulSoup

global product_count
product_count = 0
all_data = []
driver = None  # Initialize a single WebDriver instance

def setup():
    if not os.path.exists("pdfs"):
        os.makedirs("pdfs")

def get_page_num(data):
    matches = re.findall(r'\b20\b', data)
    last_match = matches[-1]
    return last_match
    

def create_driver():
    options = webdriver.FirefoxOptions()
    # Configure your options here if needed
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    return driver

def download_pdf(name):
    button = driver.find_element(By.CLASS_NAME, "d-flex")
    button.click()
    time.sleep(6)
    cwd = os.getcwd()
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.typewrite(f"{cwd}\\pdfs\\{name}", interval=0.1)
    time.sleep(1)
    pyautogui.press('enter')
    pyautogui.press('enter')
    time.sleep(5)

def scrape_pdf(url, data):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    pdf_name_tag = soup.find('h5', class_='viewer__title')
    pdf_name = ''.join(pdf_name_tag.find_all(text=True, recursive=False))
    pdf_name = pdf_name.replace(" ", "")
    page_no_tag = soup.find('div', attrs={'xpath':'//*[@id="viewer"]/nav/div/div[1]'})
    page_no = get_page_num(page_no_tag.text)
    faq = dict()
    questions_div = soup.find_all('div', attrs={'class':'faq__row'})
    for q in questions_div:
        question = q.find('h4').text
        answer = q.find('div').text
        faq[question] = answer
    data['pdf_name'] = pdf_name
    data['FAQ'] = faq
    download_pdf(pdf_name)

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

def scrape_data(url, only_5):
    global product_count
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    products = soup.find_all('div', attrs={'class': 'product-listing__item d-flex justify-content-between align-items-center pl-0'})
    print("products:", len(products))
    for product in products:
        print(product_count)
        product_count += 1
        if only_5 and product_count > 5:
            break
        product_url = product.find('a').get('href')
        print("https://www.manua.ls" + product_url)
        data = dict()
        try:
            scrape_pdf("https://www.manua.ls" + product_url, data)
        except Exception as e:
            print("Something wrong with:", "https://www.manua.ls" + product_url)
            print(e)
        scrape_info("https://www.manua.ls" + product_url.replace("manual", "specifications"), data)
        print(data)
        all_data.append(data)
        df = pd.DataFrame(all_data)
        df.to_csv('data.csv', index=False)

def run(url):
    global driver
    setup()
    driver = create_driver()
    main_url = url
    scrape_data(main_url, only_5=True) #scrape only five product
    driver.quit()

run('https://www.manua.ls/audio/microphones') # run function can scrape all detali from all product that available at given url
