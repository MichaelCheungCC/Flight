from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
 
from webdriver_manager.chrome import ChromeDriverManager
 
from datetime import datetime, timedelta
import tomli
import warnings
import urllib.parse
import csv
import logging
import os
 
warnings.simplefilter(action='ignore', category=FutureWarning)
 
project_dir = os.path.dirname(os.path.abspath(__file__))
process_datetime=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
process_date = datetime.now().strftime("%Y%m%d")
 
with open(os.path.join(project_dir, "config.toml"), "rb") as f:
    toml_dict = tomli.load(f)
 
search_type = toml_dict["web_scraping"]["SearchType"]
original_station = toml_dict["web_scraping"]["OriginStation"]
destination_station = toml_dict["web_scraping"]["DestinationStation"]
adults = toml_dict["web_scraping"]["Adults"]
children = toml_dict["web_scraping"]["Children"]
infants = toml_dict["web_scraping"]["Infants"]
currency = toml_dict["web_scraping"]["Currency"]
day_to_scrape = toml_dict["web_scraping"]["DaysToScrape"]
 
log_path = os.path.join(project_dir, toml_dict["path"]["log_path"])
log_name = toml_dict["path"]["log_name"] + process_datetime
csv_path = os.path.join(project_dir, toml_dict["path"]["csv_path"])
csv_name = toml_dict["path"]["csv_name"] + f"{original_station}_{destination_station}_{process_date}"
 
logging.basicConfig(level=logging.WARN, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y/%m/%d %H:%M:%S",
                handlers=[logging.FileHandler(f"{log_path}/{log_name}.log")])
 
 
fields = ['search_date', 'departure_date', 'departure_time', 'arrival_time', 'duration', 'departure_airport', 'arrival_airport', 'flight_code',
          'departure_terminal', 'arrival_terminal', 'departure_airport_code', 'arrival_airport_code', 'currency', 'price', 'discount',
          'search_type', 'search_departure_station', 'search_arrival_station', 'search_no_of_adults', 'search_no_of_children', 'search_no_of_infants',
          'search_currency', 'search_days_scraped', 'process_datetime']
 
 
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.maximize_window()
 
 
def get_elements(driver, selector, waiting_time=20, location=None):
    location = location if location is not None else driver
    element_present = EC.presence_of_element_located((By.XPATH, selector))
    WebDriverWait(driver, waiting_time).until(element_present)
    return location.find_elements(By.XPATH, selector)
 
def wait_until_any(driver, waiting_time=20, location=None, *selectors):
    location = location if location is not None else driver
    try:
        conditions = [EC.presence_of_element_located((By.XPATH, selector)) for selector in selectors]
        WebDriverWait(driver, waiting_time).until(EC.any_of(*conditions))
        return True
    except TimeoutException:
        False
 
def extract_flight_details(flight_webelement, flight_dict):
    flight_dict['departure_time'] = flight_webelement.find_element(By.CSS_SELECTOR, '.colDeparture .time').text
    flight_dict['arrival_time'] = flight_webelement.find_element(By.CSS_SELECTOR, '.colReturn .time').text
    flight_dict['duration'] = flight_webelement.find_element(By.CSS_SELECTOR, '.colDuration .time').text.replace("flight duration\n", "")
    flight_dict['departure_airport'] = flight_webelement.find_element(By.CSS_SELECTOR, '.colDeparture .airport-city').text
    flight_dict['arrival_airport'] = flight_webelement.find_element(By.CSS_SELECTOR, '.colReturn .airport-city').text
    flight_dict['flight_code'] = flight_webelement.find_element(By.CSS_SELECTOR, '.colDuration .flight-number').text
    flight_dict['departure_terminal'] = flight_webelement.find_element(By.CSS_SELECTOR, '.colDeparture .airport-terminal').text
    flight_dict['arrival_terminal'] = flight_webelement.find_element(By.CSS_SELECTOR, '.colReturn .airport-terminal').text
    flight_dict['departure_airport_code'] = flight_webelement.find_element(By.CSS_SELECTOR, '.colDeparture .airport-code').text
    flight_dict['arrival_airport_code'] = flight_webelement.find_element(By.CSS_SELECTOR, '.colReturn .airport-code').text
    flight_dict['currency'] = flight_webelement.find_element(By.CSS_SELECTOR, '.colPrices .currency').text
    flight_dict['price'] = flight_webelement.find_element(By.CSS_SELECTOR, '.colPrices .price').text
    return flight_dict
 
def insert_flight_search_criteria(flight_dict):
    flight_dict['search_type'] = search_type
    flight_dict['search_departure_station'] = original_station
    flight_dict['search_arrival_station'] = destination_station
    flight_dict['search_no_of_adults'] = adults
    flight_dict['search_no_of_children'] = children
    flight_dict['search_no_of_infants'] = infants
    flight_dict['search_currency'] = currency
    flight_dict['search_days_scraped'] = day_to_scrape
    return flight_dict
 
 
with open(f"{csv_path}/{csv_name}.csv", mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    for i in range(day_to_scrape):
        departure_date = (datetime.now() + timedelta(days=i+1)).strftime("%Y%m%d")
        departure_date_url = (datetime.now() + timedelta(days=i+1)).strftime("%#d%%2F%#m%%2F%Y")
        base_url = f"https://booking.hkexpress.com/en-us/select/?SearchType={search_type}&OriginStation={original_station}&DestinationStation={destination_station}&DepartureDate={departure_date_url}&Adults={adults}&Children={children}&Infants={infants}&rediscoverbooking=false&currency={currency}"
        encoded_url = urllib.parse.quote(base_url, safe=':/?&#=-%')
        driver.get(encoded_url)

        selectors = ["//header[@class='flightselect_header']", "//div[@class='larger queueElement']"]
        if wait_until_any(driver, 20, None, *selectors):
            # hit queue
            try:
                driver.find_element(By.XPATH, "//div[@class='larger queueElement']")
            except NoSuchElementException:
                pass
            else:
                logging.warn("Queue is needed.")
                exit()
           
            # sold out
            try:
                driver.find_element(By.XPATH, "//div[@class='flights_noresults']")
            except NoSuchElementException:
                pass
            else:
                logging.warn(f"{original_station} to {destination_station} on {departure_date}: Sold out or not available.")
                continue
           
            # start scraping
            try:
                flight_webelements_normal = get_elements(driver, "//div[@class='rowFlight']", waiting_time=1)
            except TimeoutException:
                pass
            else:
                for flight_webelement in flight_webelements_normal:
                    flight_dict = {'search_date': process_date, 'departure_date': departure_date}
                    flight_dict = extract_flight_details(flight_webelement, flight_dict)
                    flight_dict['discount'] = 'N'
                    flight_dict = insert_flight_search_criteria(flight_dict)
                    flight_dict['process_datetime'] = datetime.now().replace(microsecond=0).isoformat()
                    writer.writerow(flight_dict)
                   
            try:  
                flight_webelements_discounted = get_elements(driver, "//div[@class='rowFlight custom-adjust-label-position']", waiting_time=1)
            except TimeoutException:
                pass
            else:
                for flight_webelement in flight_webelements_discounted:
                    flight_dict = {'search_date': process_date, 'departure_date': departure_date}
                    flight_dict = extract_flight_details(flight_webelement, flight_dict)
                    flight_dict['discount'] = 'Y'
                    flight_dict = insert_flight_search_criteria(flight_dict)
                    flight_dict['process_datetime'] = datetime.now().replace(microsecond=0).isoformat()
                    writer.writerow(flight_dict)
        else:
            logging.warning(f"{original_station} to {destination_station} on {departure_date}: Loading is incomplete: {base_url}")
            continue