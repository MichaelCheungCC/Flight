from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from webdriver_manager.chrome import ChromeDriverManager

from datetime import datetime, timedelta
import tomli
import warnings
import urllib.parse
import csv


warnings.simplefilter(action='ignore', category=FutureWarning)

with open("config.toml", "rb") as f:
    toml_dict = tomli.load(f)

search_type = toml_dict["web_scraping"]["SearchType"]
original_station = toml_dict["web_scraping"]["OriginStation"]
destination_station = toml_dict["web_scraping"]["DestinationStation"]
adults = toml_dict["web_scraping"]["Adults"]
children = toml_dict["web_scraping"]["Children"]
infants = toml_dict["web_scraping"]["Infants"]
currency = toml_dict["web_scraping"]["Currency"]
day_to_scrape = toml_dict["web_scraping"]["DaysToScrape"]

fields = ['departure_date', 'departure_time', 'arrival_time', 'duration', 'departure_airport', 'arrival_airport', 'flight_code',
          'departure_terminal', 'arrival_terminal', 'departure_airport_code', 'arrival_airport_code', 'currency', 'price', 'process_datetime'
          , 'search_type', 'search_no_of_adults', 'search_no_of_children', 'search_no_of_infants']

process_date = datetime.now().strftime("%Y%m%d")
process_datetime = datetime.now().replace(microsecond=0).isoformat()

csv_file = f'flight_data\\flight_data_{process_date}.csv'

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.maximize_window()


def get_elements(driver, selector, waiting_time=20, location=None):
    location = location if location is not None else driver
    element_present = EC.presence_of_element_located((By.XPATH, selector))
    WebDriverWait(driver, waiting_time).until(element_present)
    return location.find_elements(By.XPATH, selector)

with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fields)

    # Write the header
    writer.writeheader()
    for i in range(day_to_scrape):
        departure_date = (datetime.now() + timedelta(days=i+1)).strftime("%Y%m%d")
        departure_date_url = (datetime.now() + timedelta(days=i+1)).strftime("%#d%%2F%#m%%2F%Y")
        base_url = f"https://booking.hkexpress.com/en-us/select/?SearchType={search_type}&OriginStation={original_station}&DestinationStation={destination_station}&DepartureDate={departure_date_url}&Adults={adults}&Children={children}&Infants={infants}&rediscoverbooking=false&currency={currency}"
        encoded_url = urllib.parse.quote(base_url, safe=':/?&#=-%')
        driver.get(encoded_url)

        try:
            flight_webelements = get_elements(driver, "//div[@class='rowFlight']")

            for flight_webelement in flight_webelements:
                flight_dict = {
                    'departure_date': departure_date,
                    'departure_time': flight_webelement.find_element(By.CSS_SELECTOR, '.colDeparture .time').text,
                    'arrival_time': flight_webelement.find_element(By.CSS_SELECTOR, '.colReturn .time').text,
                    'duration': flight_webelement.find_element(By.CSS_SELECTOR, '.colDuration .time').text.replace("flight duration\n",""),
                    'departure_airport': flight_webelement.find_element(By.CSS_SELECTOR, '.colDeparture .airport-city').text,
                    'arrival_airport': flight_webelement.find_element(By.CSS_SELECTOR, '.colReturn .airport-city').text,
                    'flight_code': flight_webelement.find_element(By.CSS_SELECTOR, '.colDuration .flight-number').text,
                    'departure_terminal': flight_webelement.find_element(By.CSS_SELECTOR, '.colDeparture .airport-terminal').text,
                    'arrival_terminal': flight_webelement.find_element(By.CSS_SELECTOR, '.colReturn .airport-terminal').text,
                    'departure_airport_code': flight_webelement.find_element(By.CSS_SELECTOR, '.colDeparture .airport-code').text,
                    'arrival_airport_code': flight_webelement.find_element(By.CSS_SELECTOR, '.colReturn .airport-code').text,
                    'currency': flight_webelement.find_element(By.CSS_SELECTOR, '.colPrices .currency').text,
                    'price': flight_webelement.find_element(By.CSS_SELECTOR, '.colPrices .price').text,
                    'search_type': search_type,
                    'search_no_of_adults': adults,
                    'search_no_of_children': children,
                    'search_no_of_infants': infants,
                    'process_datetime': process_datetime,
                }
                writer.writerow(flight_dict)

        except:
            print(f"Sold out: {original_station} to {destination_station} on {departure_date}")