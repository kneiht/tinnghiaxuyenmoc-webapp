
from django import template
from django.urls import reverse

from app_dashboard.models import Thumbnail

register = template.Library()
from datetime import date, time, datetime
from core import settings

from ..models import *
from ..utils import *

from django.shortcuts import render

@register.simple_tag
def get_static_version():
    return settings.STATIC_VERSION


import base64, json
@register.simple_tag
def encode_params(**kwargs):
    params = kwargs
    # Filter out keys with None or 'None' values
    filtered_params = {key: str(value) if isinstance(value, date) else value for key, value in params.items() if value not in [None, 'None', '']}
    # convert to json
    
    json_params = json.dumps(filtered_params)
    # Convert string to bytes
    byte_string = json_params.encode('utf-8')
    # Base64 encode the byte string
    encoded_string = base64.b64encode(byte_string)
    # Convert back to string from bytes
    query_string = encoded_string.decode('utf-8')
    return query_string



@register.filter(name='get_unique_values')
def get_unique_values(model, group_by):
    print(model, group_by)
    # get model_class
    model_class = globals()[model]
    # get all values of the field
    values = model_class.objects.values_list(group_by, flat=True)
    # get unique values
    unique_values = set(values)
    # remove None values
    unique_values = [value for value in unique_values if value != None]
    # order
    try:
        unique_values = sorted(unique_values)
    except Exception as e:
        print(e)
    print(unique_values)
    return unique_values





@register.filter(name='get_value')
def get_value(record, field):
    return getattr(record, field)

@register.filter(name='get_sign')
def get_sign(record, field):
    value = getattr(record, field)
    if value >= 0:
        return "+"
    else:
        return "-"

@register.filter(name='format_display')
def format_display(record, field=None):
    if hasattr(record, 'get_{}_display'.format(field)):
        return getattr(record, 'get_{}_display'.format(field))()
    
    if record == None:
        return ""
    if field != None:
        value = getattr(record, field)
        if value == None:
            return ""
    else:
        value = record

    if field in ['duration_seconds','overtime','holiday_time', 'normal_working_time', 'sunday_working_time']:
        if value in [None,'',0]:
            return "00:00:00"
        if value < 0:
            value = value * -1

        hours = value // 3600
        minutes = (value % 3600) // 60
        seconds = value % 60
        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

    if field in {'unit_price', 'total_amount'}:
        return "{:,}".format(int(value))
    
    _type = type(value)
    if _type == date:
        return value.strftime("%d/%m/%Y")
    elif _type == time:
        return value.strftime("%H:%M:%S")
    elif _type == datetime:
        return value.strftime("%d/%m/%Y %H:%M:%S")
    elif _type == int:
        return "{:,}".format(value)
    elif _type == float:
        return "{:,}".format(value)
    else:
        return value




@register.filter(name='format_money')
def format_money(value):
    numner = get_valid_int(value)
    return "{:,}".format(numner)




@register.filter
def get_field_value(obj, field_name):
    return getattr(obj, field_name)



import qrcode
import qrcode.image.svg
from django.utils.safestring import mark_safe

@register.simple_tag
def qr_from_text(text):
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(text, image_factory = factory)
    return mark_safe(img.to_string(encoding='unicode'))

@register.simple_tag
def get_thumbnail(image_url):
    if Thumbnail.objects.filter(reference_url=image_url).exists():
        try:
            thumbnail_url = Thumbnail.objects.filter(reference_url=image_url).first().thumbnail.url
        except Exception as e:
            thumbnail_url = str(e)
       
    else:
        thumbnail_url = 'no_thumbnail_found'
     
    return thumbnail_url




# TAGS FOR VEHICLE OPERATION RECORD
@register.filter(name='calculate_operation_duration')
def calculate_operation_duration(vehicle_operation_records):
    
    if vehicle_operation_records:
        time_seconds = vehicle_operation_records.aggregate(models.Sum('duration_seconds'))['duration_seconds__sum']
        # convert to hours, minutes, seconds
        hours = time_seconds // 3600
        minutes = (time_seconds % 3600) // 60
        seconds = time_seconds % 60
        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    else:
        return "00:00:00"   


@register.inclusion_tag('components/calculate_driver_salary.html')
def calculate_driver_salary(vehicle_operation_records, driver_name):
    def get_vehicle_types(vehicle_operation_records):
        records = vehicle_operation_records
        if not records:
            return []
        gps_names = records.values_list('vehicle', flat=True).distinct()
        vehicle_types = []
        for gps_name in gps_names:
            vehicle = VehicleDetail.objects.get(gps_name=gps_name)
            #check if the vehicle_type is already in the list
            if vehicle.vehicle_type not in vehicle_types:
                vehicle_types.append(vehicle.vehicle_type)
        return vehicle_types


    def get_start_end_of_the_month(month, year):
        # Start of the month
        start_date_of_month = datetime(year, month, 1)
        # Calculate the end of the month by moving to the next month and subtracting one day
        if month == 12:
            end_date_of_month = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date_of_month = datetime(year, month + 1, 1) - timedelta(days=1)
        return start_date_of_month.date(), end_date_of_month.date()


    def get_driver_salary_inputs(driver):
        records = vehicle_operation_records
        # Get the date of the first record
        start_time = records.first().start_time
        # Start of the month
        start_date_of_month = datetime(start_time.year, start_time.month, 1)
        # Calculate the end of the month by moving to the next month and subtracting one day
        if start_time.month == 12:
            end_date_of_month = datetime(start_time.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date_of_month = datetime(start_time.year, start_time.month + 1, 1) - timedelta(days=1)

        driver_salary_inputs = DriverSalaryInputs.objects.filter(driver=driver, valid_from__lte=end_date_of_month)
        # get the latest
        driver_salary_input = driver_salary_inputs.order_by('-valid_from').first()
        return driver_salary_input


    def calculate_monthly_salary(records, driver_salary_input):
        if not records:
            return {}
        # Get the date of the first record
        start_time = records.first().start_time
        # Get the month of the first record
        month = start_time.month
        year = start_time.year

        # Get list of all the dates from start_time of the records then remove duplicates
        working_dates = list(set([record.start_time.date() for record in records]))
        print('>>>> working_dates', working_dates)
        SUNDAY = 6
        count_days_of_month = 0
        count_sundays_of_month = 0

        count_sunday_working_days = 0
        count_holiday_working_days = 0
        count_normal_working_days = 0

        count_working_days = 0

        start_date, end_date = get_start_end_of_the_month(month, year)
        # Loop through each day from start_date to end_date
        current_date = start_date
        while current_date <= end_date:
            
            count_days_of_month += 1
            if current_date.weekday() == SUNDAY:
                count_sundays_of_month += 1
                
            if current_date in working_dates:
                count_working_days += 1
                if current_date.weekday() == SUNDAY:
                    if Holiday.is_holiday(current_date):
                        count_holiday_working_days += 1
                    else:
                        count_sunday_working_days += 1
                else: # Not sunday
                    if Holiday.is_holiday(current_date):
                        count_holiday_working_days += 1
                    else:
                        count_normal_working_days += 1
            else: # not working day
                if current_date.weekday() == SUNDAY:
                    if Holiday.is_holiday(current_date):
                        pass # Không tính gì cả
                    else: # Not sunday
                        pass # Không tính gì cả
                else: # Not sunday
                    if Holiday.is_holiday(current_date):
                        count_normal_working_days += 1
                    else:
                        pass # Không tính gì cả

            current_date += timedelta(days=1)
        print('>>>> count_normal_working_days', count_normal_working_days)

        if driver_salary_input.calculation_method == 'type_1':
            total_normal_working_days_salary = \
                    driver_salary_input.basic_month_salary \
                    * (count_normal_working_days / (count_days_of_month - count_sundays_of_month))
            
            total_sunday_working_days_salary = \
                    driver_salary_input.basic_month_salary * driver_salary_input.sunday_month_salary_percentage \
                    * (count_sunday_working_days / count_days_of_month) \
                    
            total_holiday_working_days_salary = \
                    driver_salary_input.basic_month_salary * driver_salary_input.holiday_month_salary_percentage \
                    * (count_holiday_working_days / count_days_of_month) \
                    

        elif driver_salary_input.calculation_method == 'type_2':
            total_normal_working_days_salary = \
                    driver_salary_input.basic_month_salary \
                    * (count_normal_working_days / count_days_of_month)
            
            total_sunday_working_days_salary = \
                    driver_salary_input.basic_month_salary * driver_salary_input.sunday_month_salary_percentage \
                    * (count_sunday_working_days / count_days_of_month) \
                    
            total_holiday_working_days_salary = \
                    driver_salary_input.basic_month_salary * driver_salary_input.holiday_month_salary_percentage \
                    * (count_holiday_working_days / count_days_of_month) \
                    

        total_monthly_salary = \
                total_normal_working_days_salary \
                + total_sunday_working_days_salary \
                + total_holiday_working_days_salary

        result = {
            'month': month,
            'year': year,
            '-----': '-------',
            'basic_month_salary': driver_salary_input.basic_month_salary,
            'sunday_month_salary_percentage': driver_salary_input.sunday_month_salary_percentage,
            'holiday_month_salary_percentage': driver_salary_input.holiday_month_salary_percentage,
            'calculation_method': driver_salary_input.calculation_method,
            '------': '------',
            'count_days_of_month': count_days_of_month,
            'count_sundays_of_month': count_sundays_of_month,
            'count_sunday_working_days': count_sunday_working_days,
            'count_holiday_working_days': count_holiday_working_days,
            'count_normal_working_days': count_normal_working_days,
            'count_working_days': count_working_days,
            '---': '---------',
            'total_normal_working_days_salary': total_normal_working_days_salary,
            'total_sunday_working_days_salary': total_sunday_working_days_salary,
            'total_holiday_working_days_salary': total_holiday_working_days_salary,
            'total_monthly_salary': total_monthly_salary,

        }
        return result

    def calculate_fuel_allowance(records):
        try:
            fuel_allowance = records.aggregate(models.Sum('fuel_allowance'))['fuel_allowance__sum']
            return fuel_allowance
        except Exception as e:
            return 0


    
    def calculate_hourly_salary(records, driver_salary_input):
        total_normal_working_hours = 0
        total_sunday_working_hours= 0
        total_holiday_working_hours = 0
        total_overtime_normal_working_hours = 0
        total_overtime_sunday_working_hours = 0
        total_overtime_holiday_working_hours = 0
        SUNDAY = 6
        for record in records:
            normal_working_seconds, overtime_seconds = record.calculate_working_time()
            
            date = record.start_time.date()
            if Holiday.is_holiday(date):
                total_overtime_holiday_working_hours += overtime_seconds
                total_holiday_working_hours += normal_working_seconds
            elif record.start_time.weekday() == SUNDAY:
                total_overtime_sunday_working_hours += overtime_seconds
                total_sunday_working_hours += normal_working_seconds
            else:
                total_overtime_normal_working_hours += overtime_seconds
                total_normal_working_hours += normal_working_seconds

        total_normal_working_hours /= 3600
        total_sunday_working_hours /= 3600
        total_holiday_working_hours /= 3600
        total_overtime_normal_working_hours /= 3600
        total_overtime_sunday_working_hours /= 3600
        total_overtime_holiday_working_hours /= 3600

        total_normal_working_hours_salary = total_normal_working_hours * driver_salary_input.normal_hourly_salary
        total_sunday_working_hours_salary = total_sunday_working_hours * driver_salary_input.sunday_hourly_salary
        total_holiday_working_hours_salary = total_holiday_working_hours * driver_salary_input.holiday_hourly_salary
        total_overtime_normal_working_hours_salary = total_overtime_normal_working_hours * driver_salary_input.normal_overtime_hourly_salary
        total_overtime_sunday_working_hours_salary = total_overtime_sunday_working_hours * driver_salary_input.sunday_overtime_hourly_salary
        total_overtime_holiday_working_hours_salary = total_overtime_holiday_working_hours * driver_salary_input.holiday_overtime_hourly_salary

        print(
            total_normal_working_hours_salary,
            total_sunday_working_hours_salary,
            total_holiday_working_hours_salary,
            total_overtime_normal_working_hours_salary,
            total_overtime_sunday_working_hours_salary,
            total_overtime_holiday_working_hours_salary
        )


        total_hourly_salary = \
            total_normal_working_hours_salary \
            + total_sunday_working_hours_salary \
            + total_holiday_working_hours_salary \
            + total_overtime_normal_working_hours_salary \
            + total_overtime_sunday_working_hours_salary \
            + total_overtime_holiday_working_hours_salary

        result = {
            'normal_hourly_salary': driver_salary_input.normal_hourly_salary,
            'normal_overtime_hourly_salary': driver_salary_input.normal_overtime_hourly_salary,
            'sunday_hourly_salary': driver_salary_input.sunday_hourly_salary,
            'sunday_overtime_hourly_salary': driver_salary_input.sunday_overtime_hourly_salary,
            'holiday_hourly_salary': driver_salary_input.holiday_hourly_salary,
            'holiday_overtime_hourly_salary': driver_salary_input.holiday_overtime_hourly_salary,
            '-----': '-------',
            'total_normal_working_hours': round(total_normal_working_hours, 3),
            'total_sunday_working_hours': round(total_sunday_working_hours, 3),
            'total_holiday_working_hours': round(total_holiday_working_hours, 3),
            'total_overtime_normal_working_hours': round(total_overtime_normal_working_hours, 3),
            'total_overtime_sunday_working_hours': round(total_overtime_sunday_working_hours, 3),
            'total_overtime_holiday_working_hours': round(total_overtime_holiday_working_hours, 3),
            'total_normal_working_hours_salary': round(total_normal_working_hours *  driver_salary_input.normal_hourly_salary, 3),
            '-------': '-----',
            'total_normal_working_hours_salary': total_normal_working_hours_salary,
            'total_sunday_working_hours_salary': total_sunday_working_hours_salary,
            'total_holiday_working_hours_salary': total_holiday_working_hours_salary,
            'total_overtime_normal_working_hours_salary': total_overtime_normal_working_hours_salary,
            'total_overtime_sunday_working_hours_salary': total_overtime_sunday_working_hours_salary,
            'total_overtime_holiday_working_hours_salary': total_overtime_holiday_working_hours_salary,
            
            'total_hourly_salary': total_hourly_salary,
        }
        return result


    if not vehicle_operation_records:
        return {"success": "false",
                "message": "Không tìm thấy dữ liệu tính toán lương cho tài xế.",
                "driver_name": driver_name
                }

    driver = vehicle_operation_records.first().driver

    vehicle_types = get_vehicle_types(vehicle_operation_records)
    hasXeChamCong = False
    for vehicle_type in vehicle_types:
        if vehicle_type.vehicle_type == "XE CHẤM CÔNG":
            vehicle_types.remove(vehicle_type)
            break

    if len(vehicle_types) == 0: # Ngoài xe chấm công, không còn xe nào khác
        pass # vẫn xử lý lương

    elif len(vehicle_types) >= 2: # Ngoài xe chấm công, tài xế còn chạy 2 loại xe khác
        return {"success": "false",
                "message": "Tài xế này chạy nhiều loại xe, chưa tính toán trường hợp này.",
                "driver_name": driver_name
                }
    else: # Chỉ có 1 loại xe
        vehicle_type = vehicle_types[0]

    driver_salary_input = get_driver_salary_inputs(driver)

    if not driver_salary_input:
        return {"success": "false",
                "message": "Chưa có công thức tính lương phù hợp cho tài xế này.",
                "driver_name": driver_name
                }

    data_hourly_salary = calculate_hourly_salary(vehicle_operation_records, driver_salary_input)
    data_monthly_salary = calculate_monthly_salary(vehicle_operation_records, driver_salary_input)
    total_fixed_allowance = \
        driver_salary_input.fixed_allowance \
        * min(1, data_monthly_salary['count_working_days'] / (data_monthly_salary['count_days_of_month'] - data_monthly_salary['count_sundays_of_month']))
    total_fuel_allowance = calculate_fuel_allowance(vehicle_operation_records)


    total_salary = data_monthly_salary['total_monthly_salary'] \
        + data_hourly_salary['total_hourly_salary'] \
        + total_fixed_allowance \
        + total_fuel_allowance \
        - driver_salary_input.insurance_amount



    data =  {
        'method_display': driver_salary_input.get_calculation_method_display(),
        'basic_salary': driver_salary_input.basic_month_salary,
        'fixed_allowance': driver_salary_input.fixed_allowance,
        'total_fixed_allowance': total_fixed_allowance,
        'insurance_amount': driver_salary_input.insurance_amount,
        'trip_salary': driver_salary_input.trip_salary,
        'fuel_allowance': total_fuel_allowance,

        'hourly_salary': data_hourly_salary,
        'monthly_salary': data_monthly_salary,
        'total_salary': total_salary,   
    }
    return {
        'success': 'true',
        'message': 'Tính toán lương thành công',
        "driver_name": driver_name,
        'data': data
    }


