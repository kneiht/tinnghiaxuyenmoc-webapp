
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


@register.filter(name='filter_by_vehicle')
def filter_by_vehicle(records, vehicle):
    return records.filter(vehicle=vehicle)

@register.filter(name='filter_by_driver')
def filter_by_driver(records, driver):
    return records.filter(driver=driver)



@register.filter(name='calcate_operation_duration')
def calcate_operation_duration(vehicle_operation_records):
    return "Tính toán sau"
    if vehicle_operation_records:
        time_seconds = vehicle_operation_records.filter(source='gps').aggregate(models.Sum('duration_seconds'))['duration_seconds__sum']
        # convert to hours, minutes, seconds
        hours = time_seconds // 3600
        minutes = (time_seconds % 3600) // 60
        seconds = time_seconds % 60
        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    else:
        return "00:00:00"



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

    if field in ['duration_seconds','overtime','holiday_time', 'normal_working_time']:
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



@register.filter(name='format_vnd')
def format_vnd(amount):
    if amount is None:
        return ""
    # Convert the number to a string and reverse it
    try:
        amount_str = str(int(amount))[::-1]
    except Exception as e:
        return e

    # Insert a dot every 3 digits
    formatted_str = '.'.join(amount_str[i:i+3] for i in range(0, len(amount_str), 3))
    # Reverse the string back and append the VND symbol
    return formatted_str[::-1].replace('-.','-') + " VNĐ"









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