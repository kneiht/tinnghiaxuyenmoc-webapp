
from django import template
from django.urls import reverse

from app_dashboard.models import Thumbnail

register = template.Library()
import datetime
from core import settings

@register.simple_tag
def get_static_version():
    return settings.STATIC_VERSION

@register.filter(name='format_display')
def format_display(record, field):
    if hasattr(record, 'get_{}_display'.format(field)):
        return getattr(record, 'get_{}_display'.format(field))()
    value = getattr(record, field)

    if field in {'unit_price', 'total_amount'}:
        return "{:,}".format(int(value))
    
    _type = type(value)
    if _type == datetime.date:
        return value.strftime("%d/%m/%Y")
    elif _type == datetime.time:
        return value.strftime("%H:%M:%S")
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



@register.filter
def multiply(value, arg):
    return value * arg



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