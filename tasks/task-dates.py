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

    # ===== CHẠY LẠI DATA TỪ NGÀY 6/1 ĐẾN 9/1 =====
    start_date = datetime(2026, 1, 6).date()  # Ngày bắt đầu: 6/1/2026
    end_date = datetime(2026, 1, 10).date()    # Ngày kết thúc: 9/1/2026
    
    # Tạo danh sách các ngày cần chạy
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    print(f"=========== Sẽ chạy cho các ngày: {date_list} ===========")
    
    total_tasks = len(vehicles) * len(date_list)
    task_count = 0
    
    for check_date in date_list:
        print("\n\n=========== check date: " + check_date + "===========")
        print("=========== run time:" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "===========")
        
        # write append to file
        with open('log.txt', 'a') as f:
            f.write("\n\n=========== check date: " + check_date + "===========\n")
            f.write("=========== run time:" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "===========\n")

        for vehicle in vehicles:
            task_count += 1
            while True:
                url = base_url + "api/get_trip_data_from_binhanh?gps_name=" + vehicle + "&check_date=" + check_date
                print('\n>>>>>>>>>> ', task_count, '/', total_tasks, ': ', vehicle, check_date)
                response = requests.get(url, verify=False)
                if "=> Success" not in response.text:
                    print("Fail getting data => Redo")
                    sleep(2)  # Đợi 2 giây trước khi thử lại
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