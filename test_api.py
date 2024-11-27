

def get_trip_data_from_binhanh(gps_name, check_date):
    
    def parse_operation_time(vehicle, data):
        operation_time = {}
        routes = data.get('Routes', [])
        if not routes:
            operation_time[vehicle] = {}
            return operation_time
        
       
        # Convert the list of routes into a DataFrame
        df = pd.DataFrame(routes)
        # Select only the required columns
        df = df[["LocalTime", "IsMachineOn"]]
        # Convert LocalTime column to datetime for easier processing
        df['LocalTime'] = pd.to_datetime(df['LocalTime'], format='%Y-%m-%dT%H:%M:%S')
        
        # Find the start and end of each consecutive IsMachineOn block
        df['change'] = (df['IsMachineOn'] != df['IsMachineOn'].shift()).cumsum()
        
        # Group by 'IsMachineOn' and 'change' to get periods of consecutive colors
        summary = df.groupby(['IsMachineOn', 'change']).agg(start_time=('LocalTime', 'first'), end_time=('LocalTime', 'last')).reset_index()
        
        # Filter to only include rows where IsMachineOn is "True"
        blue_summary = summary[summary['IsMachineOn'] == True].copy()  # Make an explicit copy
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


    # Define the API endpoint
    url = "http://api.gps.binhanh.vn/api/gps/route"

    # Define the payload (parameters)
    # from_date="2024-11-18T00:00:00", to_date="2024-11-18T17:30:00"
    payload = {
        "CustomerCode": "71735_6",  # Replace with your customer code
        "key": "Ff$BkG1rAu",                # Replace with your API key
        "vehiclePlate": gps_name,             # Replace with the vehicle plate
        "fromDate": check_date + "T00:00:00",    # Replace with the desired start date and time
        "toDate": check_date + "T23:59:59"      # Replace with the desired end date and time
    }

    # Define the headers (optional, if needed)
    headers = {"Content-Type": "application/json"}
    print('\n>>>> Get data for vehicle: ', gps_name, ' on date: ', check_date)
    try:
        # Make the POST request
        response = requests.post(url, json=payload, headers=headers)
        # Check the status code
        if response.status_code == 200:
            data = response.json()
            print
            # operation_time = parse_operation_time(gps_name, data)
            # result = save_operation_record(operation_time)
        else:
            result = 'Request failed with status code: ' + str(response.status_code)
            result += '\nResponse: ' + str(response.text)
            print(result)
            return  HttpResponse(result)

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        result = 'An error occurred: ' + str(e)
        return HttpResponse(result)


get_trip_data_from_binhanh()