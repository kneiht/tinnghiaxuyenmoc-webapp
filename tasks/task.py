# -*- coding: utf-8 -*-


import requests
from datetime import datetime, timedelta
import requests, json
import os
from time import sleep
import pytz

def get_date():
    """Lấy ngày hiện tại theo múi giờ Việt Nam (Asia/Ho_Chi_Minh)"""
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(vietnam_tz)
    return current_time.date()

def get_list_vehicles():
    url = base_url + 'api/get_vehicle_list_from_binhanh'
    response = requests.get(url, verify=False)
    print(response.json())
    return response.json()

def run():
    vehicles = get_list_vehicles()

    vehicles = [vehicle for vehicle in vehicles if not vehicle.startswith("72")]

    count = 0
    today_date = get_date()
    yesterday = today_date - timedelta(days=1)
    yesterday = yesterday.strftime("%Y-%m-%d")

    # RE RUN THE PREVIOUS DAY
    check_date = today_date - timedelta(days=2)
    check_date = check_date.strftime("%Y-%m-%d")
    print("=========== check date: " + check_date + "===========")
    print("=========== run time:" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "===========")
    # write append to file
    with open('log.txt', 'a') as f:
        # write to file
        f.write("\n\n=========== check date: " + check_date + "===========\n")
        f.write("=========== run time:" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "===========\n")

    for vehicle in vehicles:
        count += 1
        while True:
            url = base_url +  "api/get_trip_data_from_binhanh?gps_name=" + vehicle + "&check_date=" + check_date
            print('\n>>>>>>>>>> ', count, '/', len(vehicles), ': ',vehicle, check_date)
            response = requests.get(url, verify=False)
            if "=> Success" not in response.text:
                print("Fail getting data => Redo")
            else:
                # write append to file
                with open('log.txt', 'a') as f:
                    f.write(response.text)
                print(response.text)
                break

    check_date = yesterday
    # write append to file
    with open('log.txt', 'a') as f:
        f.write("\n\n=========== check date: " + check_date + "===========\n")
        f.write("=========== run time:" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "===========\n")


    for vehicle in vehicles:
        count += 1
        while True:
            url = base_url +  "api/get_trip_data_from_binhanh?gps_name=" + vehicle + "&check_date=" + check_date
            print('\n>>>>>>>>>> ', count, '/', len(vehicles), ': ',vehicle, check_date)
            response = requests.get(url, verify=False)
            if "=> Success" not in response.text:
                print("Fail getting data => Redo")
            else:
                # write append to file
                with open('log.txt', 'a') as f:
                    f.write(response.text)
                print(response.text)
                break

base_url_local = 'http://127.0.0.1:8000/'
base_url_online = 'https://quanly.tinnghiaxuyenmoc.com/'
base_url = base_url_online

print("=========== run time:" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "===========")
flag = True
count = 0
while flag:
    try:
        run()
        flag = False
    except Exception as e:
        print(e)
        print("Fail getting data => Redo")
        sleep(5)
        flag = True
        count += 1
        if count == 3:
            break