
from django import template
from django.urls import reverse

from app_dashboard.models import Thumbnail

register = template.Library()
from datetime import date, time, datetime
from core import settings

from ..models import *


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






@register.filter(name='group')
def group(records, field):
    # get all values of the field
    values = [getattr(record, field) for record in records]
    # get unique values
    unique_values = set(values)
    # remove None values
    unique_values = [value for value in unique_values if value != None]
    # order
    try:
        unique_values = sorted(unique_values)
    except Exception as e:
        print(e)
    return unique_values






# TAGS FOR VEHICLE OPERATION RECORD
@register.filter(name='calcate_operation_duration')
def calcate_operation_duration(vehicle_operation_records):
    if vehicle_operation_records:
        time_seconds = vehicle_operation_records.aggregate(models.Sum('duration_seconds'))['duration_seconds__sum']
        # convert to hours, minutes, seconds
        hours = time_seconds // 3600
        minutes = (time_seconds % 3600) // 60
        seconds = time_seconds % 60
        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    else:
        return "00:00:00"


@register.simple_tag
def calculate_salary(vehicle_operation_records, start_date, end_date):
    def format_number(number):
        return "{:,}".format(int(number))
    
    def calculate_fuel_allowance(records):
        try:
            fuel_allowance = records.aggregate(models.Sum('fuel_allowance'))['fuel_allowance__sum']
            return fuel_allowance
        except Exception as e:
            return 0

    def calculate_hourly_salary(records, time_string=None):
        if time_string == 'normal_working_time':
            percentage = 1
        elif time_string == 'overtime':
            percentage = driver.overtime_percentage
        elif time_string == 'sunday_working_time':
            percentage = driver.sunday_percentage
        elif time_string == 'holiday_time':
            percentage = driver.holiday_percentage
        else:
            return 1

        try:
            time_seconds = records.aggregate(models.Sum(time_string))[f'{time_string}__sum']
            time_hours = time_seconds / 3600
            salary = time_hours * driver.hourly_salary * percentage
            format_salary = format_number(salary)
            result = {
                'hourly_salary': driver.hourly_salary,
                'salary': salary,
                'format_salary': format_salary,
                'time_hours': time_hours,
                'percentage': percentage}
            return result
        except Exception as e:
            result = {
                'hourly_salary': 0,
                'salary': 0,
                'format_salary': 0,
                'time_hours': 0,
                'percentage': 1}
            return result

    records = vehicle_operation_records
    driver = records.first().driver
    # Count days
    # date string convert to type date
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    days_count = (end_date - start_date).days + 1

    # Count the number of days that the driver works by getting the list of dates (from starttime)
    dates = [record.start_time.date() for record in records]
    working_days_count = len(set(dates))

    actual_basic_salary = driver.basic_salary * working_days_count / days_count
    fuel_allowance = calculate_fuel_allowance(records)
    fixed_allowance = driver.fixed_allowance * working_days_count/days_count
    insurance = driver.insurance_amount * working_days_count/days_count
    normal_working_time_salary = calculate_hourly_salary(records, 'normal_working_time')
    overtime_salary = calculate_hourly_salary(records, 'overtime')
    sunday_working_time_salary = calculate_hourly_salary(records, 'sunday_working_time')
    holiday_time_salary = calculate_hourly_salary(records, 'holiday_time')
    sum_salary = actual_basic_salary + normal_working_time_salary['salary'] + overtime_salary['salary'] + \
        sunday_working_time_salary['salary'] + holiday_time_salary['salary'] + \
        fuel_allowance + fixed_allowance - insurance

    result = ''
    result += f'Lương cơ bản: {format_number(driver.basic_salary)} VNĐ\n'
    result += f'1. Số ngày làm việc: {working_days_count}/{days_count} => Lương cơ bản nhận: {format_number(actual_basic_salary)} VNĐ\n' 
    temp = normal_working_time_salary['format_salary']
    result += f'2. Lương giờ bình thường => {temp} VNĐ\n'
    temp = overtime_salary['format_salary']
    result += f'3. Lương giờ tăng ca: {temp} VNĐ\n'
    temp = sunday_working_time_salary['format_salary']
    result += f'4. Lương giờ chủ nhật: {temp} VNĐ\n'
    temp = holiday_time_salary['format_salary']
    result += f'5. Lương giờ lễ: {temp} VNĐ\n'

    result += f'6. Phụ cấp xăng: {format_number(fuel_allowance)} VNĐ\n'
    result += f'7. Phụ cấp cố định: {format_number(fixed_allowance)} VNĐ\n'
    result += f'8. BHXH: {format_number(insurance)} VNĐ\n'
    result += f'Tổng lương (1+2+3+4+5+6+7 - 8): {format_number(sum_salary)} VNĐ'
    return result.strip()



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
def format_display(record, field):
    if hasattr(record, 'get_{}_display'.format(field)):
        return getattr(record, 'get_{}_display'.format(field))()
    
    if record == None:
        return ""
    value = getattr(record, field)
    if value == None:
        return ""

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