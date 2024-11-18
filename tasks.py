# -*- coding: utf-8 -*-


import requests
from datetime import datetime
import requests, json

# Create a post request to send data to the server
def call_api_to_save_operation_data(vehicle, check_date):
    if DOMAIN == "localhost":
        base_url = 'http://127.0.0.1:8000/'
    else:
        base_url = 'https://www.tinnghiaxuyenmoc.com/'
    
    # data in the body is check_date
    data = {
        'check_date': check_date
    }
    response = requests.post(url, data=data)
    return response


# Load from a file
with open("env.json", "r") as f:
    env = json.load(f)
DOMAIN = env["domain"]

if DOMAIN == "localhost":
    base_url = 'http://127.0.0.1:8000/'
else:
    base_url = 'https://www.tinnghiaxuyenmoc.com/'


def get_list_vehicles():
    url = base_url + 'api/get_vehicle_list_from_binhanh'
    response = requests.get(url)
    return response.json()


# vehicles = get_list_vehicles()
# count = 0
# for vehicle in vehicles:
#     count += 1
#     check_date = datetime.now().strftime("%Y-%m-%d")
#     url = base_url +  "api/get_trip_data_from_binhanh?gps_name=" + vehicle + "&check_date=" + check_date
#     print('\n>>>>>>>>>> ', count, '/', len(vehicles), ': ',vehicle, check_date)
#     response = requests.get(url)
#     print(response.text)


vehicles = get_list_vehicles()
for day in range(1,19):
    count = 0
    for vehicle in vehicles:
        count += 1
        check_date = '2024-11-' + str(day).zfill(2)
        url = base_url +  "api/get_trip_data_from_binhanh?gps_name=" + vehicle + "&check_date=" + check_date
        print('\n>>>>>>>>>> ', count, '/', len(vehicles), ': ',vehicle, check_date)
        response = requests.get(url)
        print(response.text)









