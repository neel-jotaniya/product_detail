from bs4 import BeautifulSoup
import requests
import pandas as pd

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

def scrape_FAQ(url, data):
    response = requests.get(url)
    if response.status_code != 200: 
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    faq = dict()
    questions_div = soup.find_all('div', attrs={'class':'faq__row'})
    for q in questions_div:
        question = q.find('h4').text
        answer = q.find('div').text
        faq[question] = answer
    data['FAQ'] = faq
    
def main(url):
    response = requests.get(url)
    all_data = []
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
            scrape_FAQ("https://www.manua.ls"+product_url, data)  #scrape FAQs
            print(data)
            all_data.append(data)
            df = pd.DataFrame(all_data)
            df.to_csv('data.csv', index=False)
        i += 1
main('https://www.manua.ls/')