# -*- coding: utf-8 -*-


import pandas as pd
import requests
from datetime import datetime
import requests, json
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup   


# # Create a post request to send data to the server
# def send_data_to_server(check_date):
#     if DOMAIN == "localhost":
#         url = 'http://127.0.0.1:8000/api/save-vehicle-operation-record'
#     else:
#         url = 'https://www.tinnghiaxuyenmoc.com/api/save-vehicle-operation-record'
    
#     # data in the body is check_date
#     data = {
#         'check_date': check_date
#     }
#     response = requests.post(url, data=data)
#     return response


# # Load from a file
# with open("env.json", "r") as f:
#     env = json.load(f)
# DOMAIN = env["domain"]


# # # Get today date
# # today = datetime.date.today()
# # check_date = today.strftime('%d/%m/%Y')
# # get_binhanh_service_operation_time('01/05/2024')

# from datetime import datetime, timedelta

# check_date = datetime.strptime('13/06/2024', '%d/%m/%Y').date()
# for i in range(0, 150):
#     # Increase check_date by 1 day
#     current_date = check_date + timedelta(days=i)
#     # Format date for display or function calls
#     formatted_date = current_date.strftime('%Y-%m-%d')
#     print(formatted_date)
#     # Call your function with the formatted date
#     response = send_data_to_server(formatted_date)

#     print(response.text)
#     # write response to a file
#     with open("response.txt", "a") as f:
#         f.write(response.text + "\n")


def call_api(url, payload):
    customer_code = '71735_6'
    api_key = 'Ff$BkG1rAu'
    auth=HTTPBasicAuth(customer_code, api_key)

    response = requests.post(
        url, 
        json=payload, 
        auth=auth
    )
    return response



def get_vehicle_list():
    # get api type from params
    url = 'http://api.gps.binhanh.vn/apiwba/gps/tracking'
    payload = {
        'IsFuel': True 
    }
    response = call_api(url, payload)
    if response.status_code == 200:
        data = response.json()  
        message_result = data.get('MessageResult')
        if message_result == 'Success':
            vehicles = data.get('Vehicles', [])
            # Extracting PrivateCode values
            private_codes = [vehicle["PrivateCode"] for vehicle in vehicles ]
            print(private_codes)
            return private_codes
        else:
            return []
    else:
        return []
    
def get_trip_data():
    # Define the API endpoint
    url = "http://api.gps.binhanh.vn/api/gps/route"

    # Define the payload (parameters)
    payload = {
        "CustomerCode": "71735_6",  # Replace with your customer code
        "key": "Ff$BkG1rAu",                # Replace with your API key
        "vehiclePlate": "XECUOC14",             # Replace with the vehicle plate
        "fromDate": "2024-11-18T07:30:00",    # Replace with the desired start date and time
        "toDate": "2024-11-18T17:30:00"       # Replace with the desired end date and time
    }

    # Define the headers (optional, if needed)
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Make the POST request
        response = requests.post(url, json=payload, headers=headers)
        # Check the status code
        if response.status_code == 200:
            data = response.json()  
            message_result = data.get('MessageResult')
            if 'Success' in message_result :
                routes = data.get('Routes', [])
                # print(data)
                # write to file
                with open("routes.txt", "a") as f:
                    f.write(str(data) + "\n")
                return routes
            else:
                return []

        else:
            print("Request failed with status code:", response.status_code)
            print("Response:", response.text)
            routes = []

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        routes = []
    
get_trip_data()
