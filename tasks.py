
import pandas as pd
import datetime

import requests, json
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup   



def get_binhanh_service_operation_time(check_date):
    # if check_date is None:
    #     check_date = datetime.now()
    
    # # convert checkdate to string dd//mm/yyyy
    # check_date_str = check_date.strftime("%d/%m/%Y")

    # Get json data
    def call_api(url, payload, auth):
        response = requests.post(
            url, 
            json=payload, 
            auth=auth
        )
        return response

    def get_vehicle_list():
        # get api type from params
        
        customer_code = '71735_6'
        api_key = 'Ff$BkG1rAu'
        auth=HTTPBasicAuth(customer_code, api_key)
        url = 'http://api.gps.binhanh.vn/apiwba/gps/tracking'
        payload = {
            'IsFuel': True  # True nếu muốn tính toán nhiên liệu
        }
        response = call_api(url, payload, auth)
        # Xử lý kết quả trả về
        if response.status_code == 200:
            data = response.json()  # Chuyển dữ liệu JSON trả về thành dict
            message_result = data.get('MessageResult')
            if message_result == 'Success':
                vehicles = data.get('Vehicles', [])
                # Extracting PrivateCode values
                private_codes = [vehicle["PrivateCode"] for vehicle in vehicles ]
                return private_codes
            else:
                return []
        else:
            return []
            
    def get_operation_time(vehicles, start_date, end_date):
        # URL for login
        url = "https://gps.binhanh.vn"

        # Start a session to persist cookies across requests
        session = requests.Session()

        # Headers for the request
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "DNT": "1",
            "Origin": "https://gps.binhanh.vn",
            "Referer": "https://gps.binhanh.vn/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"'
        }

        # Step 1: Get the initial login page to retrieve `__VIEWSTATE`, `__VIEWSTATEGENERATOR`, and `__EVENTVALIDATION`
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the dynamic fields
        viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
        viewstate_generator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
        event_validation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]

        # Step 2: Prepare the payload for login
        data = {
            "__LASTFOCUS": "",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstate_generator,
            "__EVENTVALIDATION": event_validation,
            "UserLogin1$txtLoginUserName": "tinnghiavt",
            "UserLogin1$txtLoginPassword": "Tinnghia1234",
            "UserLogin1$hdfPassword": "",
            "UserLogin1$btnLogin": "Đăng nhập",
            "UserLogin1$txtPhoneNumberOtp": "",
            "UserLogin1$txtOTPClient": "",
            "UserLogin1$hdfOTPServer": "",
            "UserLogin1$hdfTimeoutOTP": ""
        }
        
        # Step 3: Send the POST request to login
        login_response = session.post(url, headers=headers, data=data)
        # Step 4: Check if login was successful by verifying redirection or specific content in the response 01/05/2024
        if login_response.ok and "OnlineM.aspx" in login_response.url:
            print("Login successful!")
            operation_time = {}
            count = 0
            for vehicle in vehicles[0:5]:
                url = f'https://gps.binhanh.vn/HttpHandlers/RouteHandler.ashx?method=getRouterByCarNumberLite&carNumber={vehicle}&fromDate={start_date}%2000:00&toDate={end_date}%2023:59&split=false&isItinerary=false'
                response = session.get(url, headers=headers)
                data = response.json().get("data")
                count += 1
                print(f'Vehicle {count}/{len(vehicles)}:', vehicle)
                # print(data)
                # print('\n\n\n')
                if data == []:
                    operation_time[vehicle] = {}
                    continue
                df = pd.DataFrame(data)
                # Select only columns 1 and 17 (index-based selection)
                df = df.iloc[:, [1, 18]]
                # Rename columns
                df.columns = ["timestamp", "color"]

                # Convert timestamp column to datetime for easier processing
                df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%m/%Y %H:%M:%S')

                # Find the start and end of each consecutive color block
                df['change'] = (df['color'] != df['color'].shift()).cumsum()

                # Group by 'color' and 'change' to get periods of consecutive colors
                summary = df.groupby(['color', 'change']).agg(start_time=('timestamp', 'first'), end_time=('timestamp', 'last')).reset_index()

                # Filter to only include rows where color is "Blue"
                blue_summary = summary[summary['color'] == 'Blue'].copy()  # Make an explicit copy
                # Convert start_time and end_time columns to datetime
                blue_summary['start_time'] = pd.to_datetime(blue_summary['start_time'])
                blue_summary['end_time'] = pd.to_datetime(blue_summary['end_time'])
                # Calculate duration in seconds
                blue_summary['duration_seconds'] = (blue_summary['end_time'] - blue_summary['start_time']).dt.total_seconds()

                # Convert start_time and end_time to string format for JSON serialization
                blue_summary['start_time'] = blue_summary['start_time'].astype(str)
                blue_summary['end_time'] = blue_summary['end_time'].astype(str)

                operation_time[vehicle] = blue_summary.to_dict(orient="records")
            return operation_time
        else:
            return []

    
    vehicles = get_vehicle_list()
    # start_date = '01/05/2024'
    # end_date = '01/05/2024'

    # Get operation time
    operation_time = get_operation_time(vehicles, check_date, check_date)
    send_data_to_server(operation_time)



# Create a post request to send data to the server
def send_data_to_server(data):
    url = 'http://127.0.0.1:8000/api/save-vehicle-operation-record'
    response = requests.post(url, json=data)
    print(response.text)


for i in range(1):
    # format dd/mm/yyyy
    check_date = (f'{i+1:02d}/05/2024')
    get_binhanh_service_operation_time(check_date)