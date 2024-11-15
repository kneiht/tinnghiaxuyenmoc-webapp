# # -*- coding: utf-8 -*-


# import pandas as pd
# import datetime

# import requests, json
# from requests.auth import HTTPBasicAuth
# from bs4 import BeautifulSoup   


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


from datetime import datetime, timedelta
def get_start_end_of_the_month(month, year):
    # Start of the month
    start_date_of_month = datetime(year, month, 1)
    # Calculate the end of the month by moving to the next month and subtracting one day
    if month == 12:
        end_date_of_month = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date_of_month = datetime(year, month + 1, 1) - timedelta(days=1)
    return start_date_of_month, end_date_of_month


start_date, end_date = get_start_end_of_the_month(5, 2024)
# Loop through each day from start_date to end_date
current_date = start_date
while current_date <= end_date:
    print(current_date)
    current_date += timedelta(days=1)