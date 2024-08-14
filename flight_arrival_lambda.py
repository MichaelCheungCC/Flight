import json
import requests
import os
import urllib
from datetime import datetime, timedelta
import csv
import boto3
import uuid


def lambda_handler(event, context):
    csv_field = ["time", "origin", "flight_no", "flight_airline", "status", "statusCode", "baggage", "hall", "terminal", "stand"]
    target_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    lang = "en"
    cargo = "false"
    arrival = "true"
    
    s3 = boto3.client('s3')

    base_url = f"https://www.hongkongairport.com/flightinfo-rest/rest/flights/past?date={target_date}&lang={lang}&cargo={cargo}&arrival={arrival}"
    encoded_url = urllib.parse.quote(base_url, safe=":/?&#=-%")

    response = requests.get(encoded_url)

    if response.status_code == 200:
        try:
            flights_info = response.json()[0]["list"]
            with open("/tmp/flight_data.csv", "w", newline="") as file:
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
                        
            upload_path = f"flight_schedule/arrival/date={target_date}/flight_arrival_{target_date}.csv"
            s3.upload_file("/tmp/flight_data.csv", "flight-data-5614489", upload_path)
            
            return {
                'statusCode': 200,
                'body': f"Successfully get and load {target_date} flight arrival data."
            }
            
        except Exception as e:
            return {
                'statusCode': 404,
                'body': str(e)
            }
            
    else:
        return {
            'statusCode': response.status_code,
            'body': f"Error in getting {target_date} flight arrival data."
        }