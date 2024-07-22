from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import time

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

driver.get("https://booking.hkexpress.com/zh-hk/select/?SearchType=ONEWAY&OriginStation=HKG&DestinationStation=TYO&DepartureDate=1%2F8%2F2024&Adults=1&rediscoverbooking=false&currency=HKD&")
time.sleep(20)

page_source = driver.page_source

soup = BeautifulSoup(page_source, 'html.parser')

paragraphs = soup.find_all('span', {'class': 'price ng-tns-c0-0 ng-star-inserted'})
for paragraph in paragraphs:
    print(paragraph.text)

driver.close()