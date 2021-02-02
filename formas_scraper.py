import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import lxml
import time
import pandas as pd


options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome("/Users/heinipartanen/Downloads/chromedriver", options=options)

url = "https://formas.se/arkiv/alla-utlysningar.html"


def get_links():
    driver.get(url)
    selection = driver.find_elements_by_class_name("sol-calls-status__item")[4]
    selection.click()
    time.sleep(3)
    i = 0
    while i < 7:
        button = driver.find_element_by_xpath('//button[text()="Visa fler"]')
        driver.execute_script("arguments[0].click();", button)
        time.sleep(2)
        i = i + 1
    page = driver.page_source
    soup2 = BeautifulSoup(page, 'lxml')
    table = soup2.find('div', {'class': 'sol-calls-list sol-col-xl-8 sol-col-lg-8 sol-col-md-12'})
    links = []
    for href in table.find_all('a'):
        links.append("https://formas.se" + href.get("href"))

    return links


def get_xlsx():
    spreadsheets = []
    for link in get_links():
        try:
            response = requests.get(link)
            call_data = BeautifulSoup(response.content, 'lxml')
            call_title = call_data.find('h1')
            excel_file = call_data.find('div', {'class': 'sol-action-link'})
            excel_link = excel_file.find('a')
            call_details = []
            if '.xlsx' in excel_link.get('href'):
                call_details.append(call_title.text)
                call_details.append("https://formas.se" + excel_link.get('href'))
            else:
                continue
            spreadsheets.append(call_details)
        except:
            continue
    return spreadsheets


def write_file():
    for file in get_xlsx():
        df = pd.read_excel(file[1], usecols=[0], header=None, engine='openpyxl').assign(call=file[0])
        df1 = df[df.iloc[:, 0].str.contains(r'\d\d\d\d-\d\d\d\d\d', na=False)]
        print(df1)
        df1.to_csv('data.csv', index=False, header=None, mode='a')


write_file()