import requests
import os
import tomli
import urllib
from datetime import datetime, timedelta
import csv

project_dir = os.path.dirname(os.path.abspath(__file__))
csv_field = ["time", "origin", "flight_no", "flight_airline", "status", "statusCode", "baggage", "hall", "terminal", "stand"]

with open(os.path.join(project_dir, "config.toml"), "rb") as f:
    toml_dict = tomli.load(f)
lang = toml_dict["flight_api"]["lang"]
cargo = "false"
arrival = "true"

for i in range(90):
    target_date = (datetime.now() - timedelta(days=i+2)).strftime("%Y-%m-%d")
    csv_dir = os.path.join(project_dir, "flight_schedule", "arrival", f"date={target_date}")
    os.makedirs(csv_dir, exist_ok=True)
    csv_file = os.path.join(csv_dir, f"flight_arrival_{target_date}.csv")

    base_url = f"https://www.hongkongairport.com/flightinfo-rest/rest/flights/past?date={target_date}&lang={lang}&cargo={cargo}&arrival={arrival}"
    encoded_url = urllib.parse.quote(base_url, safe=":/?&#=-%")

    response = requests.get(encoded_url)

    if response.status_code == 200:
        try:
            flights_info = response.json()[0]["list"]
        except Exception as e:
            print(e)
            continue
    else:
        print("Failed to fetch data. Status code:", response.status_code)
        continue

    with open(csv_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(csv_field)

        for flights in flights_info:
            for flight in flights["flight"]:
                row = [
                    flights["time"],
                    flights["origin"],
                    flight["no"],
                    flight["airline"],
                    flights["status"],
                    flights["statusCode"],
                    flights["baggage"],
                    flights["hall"],
                    flights["terminal"],
                    flights["stand"]
                ]
                writer.writerow(row)