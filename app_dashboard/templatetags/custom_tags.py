from django import template
from django.urls import reverse

from app_dashboard.models.models import Thumbnail

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


@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return value * arg
    except:
        return 0


@register.filter(name='get_unique_values')
def get_unique_values(model, group_by):
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
    return unique_values


@register.filter(name='get_project_role')
def get_project_role(project, user):
    project_user = ProjectUser.objects.filter(project=project, user=user).first()
    if project_user == None:
        return "normal_staff"
    return project_user.role


@register.filter(name='get_value')
def get_value(record, field):
    if type(record) == dict:
        return record.get(field)
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

    if field == 'allow_overtime' or field == 'allow_revenue_overtime':
        if value:
            return "Cho phép"
        else:
            return "Không cho phép"

    if field in {'unit_price', 'total_amount', 'amount'}:
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
def calculate_vehicle_part_total_purchase(vehice_parts):
    total = 0
    for vehice_part in vehice_parts:
        total += vehice_part.quantity * vehice_part.repair_part.part_price
    return format_money(total)


def format_money_PL(value):
    number = value
    return "{:,.2f}".format(number)

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
@register.inclusion_tag('components/calculate_total_operation_time.html')
def calculate_total_operation_time(vehicle_operation_records, gps_name):
    def format_time(time_seconds):
        if time_seconds == None:
            return "00:00:00"
        hours = time_seconds // 3600
        minutes = (time_seconds % 3600) // 60
        seconds = time_seconds % 60
        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    
    if not vehicle_operation_records:
        return {"success": "false",
                "message": "Không tìm thấy dữ liệu",
                "gps_name": gps_name
                }
    

    total_vehicle_time_seconds = vehicle_operation_records.aggregate(models.Sum('duration_seconds'))['duration_seconds__sum']
    # calculate total time which has driver
    total_driver_time_seconds = vehicle_operation_records.filter(driver__isnull=False).aggregate(models.Sum('duration_seconds'))['duration_seconds__sum']

    # get the list of driver
    drivers = vehicle_operation_records.filter(driver__isnull=False).values_list('driver', flat=True).distinct()
    unique_values = set(drivers)
    

    driver_working_times = []
    unallowed_revenue_overtime = 0
    for driver in unique_values:
        total_normal_woring_time = 0
        total_overtime = 0
        filtered_records = vehicle_operation_records.filter(driver=driver)
        for filtered_record in filtered_records:
            normal_woring_time, overtime = filtered_record.calculate_working_time()

            if not filtered_record.allow_revenue_overtime:
                unallowed_revenue_overtime += overtime

            if not filtered_record.allow_overtime:
                overtime = 0

            total_normal_woring_time += normal_woring_time
            total_overtime += overtime

        driver_working_times.append({
            'driver': StaffData.objects.get(pk=driver).full_name,
            'total_normal_woring_time': format_time(total_normal_woring_time),
            'total_overtime': format_time(total_overtime)
        })

    if total_driver_time_seconds == None:
        total_driver_time_seconds = 0
    if total_vehicle_time_seconds == None:
        total_vehicle_time_seconds = 0

    data = {
        "total_vehicle_time": format_time(total_vehicle_time_seconds),
        "total_driver_time": format_time(total_driver_time_seconds - unallowed_revenue_overtime),
        "total_vehicle_time_seconds": total_vehicle_time_seconds,
        "total_driver_time_seconds": total_driver_time_seconds - unallowed_revenue_overtime,
        "gps_name": gps_name,
        "driver_working_times": driver_working_times
    }
    return {
        'success': 'true',
        'message': 'Tính toán thời gian thành công',
        "gps_name": gps_name,
        'data': data,
        'drivers': drivers
    }



@register.inclusion_tag('components/calculate_driver_salary.html')
def calculate_driver_salary(vehicle_operation_records, driver_name, select_start_date=None, select_end_date=None):
    if not vehicle_operation_records:
        return {"success": "false",
                "message": "Không tìm thấy dữ liệu",
                "driver_name": driver_name
                }

    # get the list of vehicle
    vehicles = vehicle_operation_records.values_list('vehicle', flat=True).distinct()
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

    def calculate_monthly_salary(records, driver_salary_input, select_start_date=None, select_end_date=None):
        # print debug records
        print("records: ", records)
        if not records:
            return {}
        # Get the date of the first record
        start_time = records.first().start_time
        # Get the month of the first record
        month = start_time.month
        year = start_time.year

        # Get list of all the dates from start_time of the records then remove duplicates
        working_dates = list(set([record.start_time.date() for record in records]))
        # Calculate paid_dates from select_start_date to select_end_date
        paid_dates = None
        if select_start_date:
            paid_dates = []
            select_start_date = datetime.strptime(select_start_date, "%Y-%m-%d").date()
            select_end_date = datetime.strptime(select_end_date, "%Y-%m-%d").date()
            current_paid_date = select_start_date
            while current_paid_date <= select_end_date:
                paid_dates.append(current_paid_date)
                current_paid_date += timedelta(days=1)

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
                if paid_dates: # chỉ tính trường hợp này cho PL
                    if current_date in paid_dates:
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
                else:
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
            if not record.allow_overtime:
                overtime_seconds = 0

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

    # TẠM THỜI TẮT TÍNH NĂNG KIỂM TRA LOẠI XE, MẶC ĐỊNH TÀI XẾ CHẠY 1 LOẠI XE, 1 LOẠI TÍNH LƯƠNG
    # vehicle_types = get_vehicle_types(vehicle_operation_records)
    # hasXeChamCong = False
    # for vehicle_type in vehicle_types:
    #     if vehicle_type == None:
    #         return {"success": "false",
    #                 "message": "Không tìm thấy dữ liệu loại xe, vui lòng thêm loại xe trong bảng Dữ liệu chi tiết từng xe.",
    #                 "driver_name": driver_name
    #                 }

    #     if vehicle_type.vehicle_type == "XE CHẤM CÔNG":
    #         vehicle_types.remove(vehicle_type)
    #         break

    # if len(vehicle_types) == 0: # Ngoài xe chấm công, không còn xe nào khác
    #     pass # vẫn xử lý lương

    # elif len(vehicle_types) >= 2: # Ngoài xe chấm công, tài xế còn chạy 2 loại xe khác
    #     return {"success": "false",
    #             "message": "Tài xế này chạy nhiều loại xe, chưa tính toán trường hợp này.",
    #             "driver_name": driver_name
    #             }
    # else: # Chỉ có 1 loại xe
    #     vehicle_type = vehicle_types[0]

    driver_salary_input = get_driver_salary_inputs(driver)

    if not driver_salary_input:
        return {"success": "false",
                "message": "Chưa có công thức tính lương phù hợp cho tài xế này.",
                "driver_name": driver_name
                }

    data_hourly_salary = calculate_hourly_salary(vehicle_operation_records, driver_salary_input)
    data_monthly_salary = calculate_monthly_salary(vehicle_operation_records, driver_salary_input, select_start_date, select_end_date)
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






# TAGS FOR VEHICLE OPERATION RECORD
@register.inclusion_tag('components/calculate_revenue_report.html')
def calculate_revenue_report(vehicle_operation_records, vehicle, select_start_date, select_end_date, update=False):
    def format_time(time_seconds):
        if time_seconds == None:
            return "00:00:00"
        hours = time_seconds // 3600
        minutes = (time_seconds % 3600) // 60
        seconds = time_seconds % 60
        return "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
    
    rows = []
    # Use vehicle_operation_records to get 2 capped dates
    min_start_date = datetime.strptime(select_start_date, '%Y-%m-%d').date()
    max_end_date = datetime.strptime(select_end_date, '%Y-%m-%d').date()

    if update:
        if vehicle_operation_records:
            gps_name = vehicle_operation_records.first().vehicle
        else:
            gps_name = vehicle

        vehicle_records = vehicle_operation_records.filter(vehicle=gps_name)
        vehicle_records_with_driver = vehicle_records.filter(driver__isnull=False)
        # get unique start_date
        unique_start_dates = vehicle_records.values_list('start_time', flat=True).distinct()
        unique_start_dates = list(unique_start_dates)
        # use map to get date only
        unique_start_dates = list(map(lambda x: x.date(), unique_start_dates))
        # get unique start_date
        unique_start_dates = set(unique_start_dates)

        revenue_base = 0
        revenue = 0
        
        total_working_hours = 0
        fuel_filling_cost_amount = 0
        other_filling_cost_amount = 0
        depreciation_amount = 0
        bank_interest_amount = 0
        maintenance_amount = 0

        revenue_base_display = ""
        vehicle_instance = VehicleDetail.objects.get(gps_name=gps_name)
        vehicle_revenue_inputs_record = VehicleRevenueInputs.objects.filter(vehicle_type=vehicle_instance.vehicle_type)
        for input_record in vehicle_revenue_inputs_record:
            revenue_base_display += "- " + input_record.valid_from.strftime("%d/%m/%Y") + ": " + str(format_money_PL(input_record.revenue_day_price)) + " VND - " + str(input_record.number_of_hours) + " giờ" + "\n"
        revenue_base_display = revenue_base_display.strip();
        
        # Because the revenue is different for each day, so we need to calculate revenue for each day
        for start_date in unique_start_dates:
            # check vehicle records for calculating time must have driver
            vehicle_records_with_driver_for_date = vehicle_records_with_driver.filter(start_time__date=start_date)
            # calculate total time which has driver
            working_time_seconds = vehicle_records_with_driver_for_date.aggregate(models.Sum('duration_seconds'))['duration_seconds__sum']
            unallowed_revenue_overtime = 0
            for record in vehicle_records_with_driver_for_date:
                normal_woring_time, overtime = record.calculate_working_time()
                if not record.allow_revenue_overtime:
                    unallowed_revenue_overtime += overtime

            if working_time_seconds == None:
                working_time_seconds = 0
            # Calculate for the case when adding data munally
            # if working_time_seconds == 0:
            #     normal_working_time_seconds = vehicle_records_with_driver_for_date.aggregate(models.Sum('normal_working_time'))['normal_working_time__sum']
            #     overtime_seconds = vehicle_records_with_driver_for_date.aggregate(models.Sum('overtime'))['overtime__sum']
            #     if normal_working_time_seconds == None:
            #         normal_working_time_seconds = 0
            #     if overtime_seconds == None:
            #         overtime_seconds = 0
            #     working_time_seconds = normal_working_time_seconds + overtime_seconds

            working_time_hours = (working_time_seconds - unallowed_revenue_overtime) /3600
            total_working_hours += working_time_hours
            
            date_vehicle_revenue_inputs_record = VehicleRevenueInputs.get_valid_record(vehicle_instance.vehicle_type, start_date)
            if not date_vehicle_revenue_inputs_record:
                revenue = "Không có dữ liệu tính doanh thu ngày  " + start_date.strftime("%d/%m/%Y")
                revenue_base = "Không có dữ liệu tính doanh thu ngày  " + start_date.strftime("%d/%m/%Y")
                break

            if date_vehicle_revenue_inputs_record.number_of_hours== 0:
                revenue = "Dữ liệu số giờ tính doanh thu 1 ngày không được bằng 0"
                revenue_base = "Dữ liệu số giờ tính doanh thu 1 ngày không được bằng 0"
                break

            # Đơn giá gần nhất
            revenue_base = date_vehicle_revenue_inputs_record.revenue_day_price
            date_revenue = (date_vehicle_revenue_inputs_record.revenue_day_price/date_vehicle_revenue_inputs_record.number_of_hours)*working_time_hours
            revenue += date_revenue


        # calculate fuel cost
        filling_records = FillingRecord.objects.filter(vehicle=vehicle_instance, fill_date__gte=min_start_date, fill_date__lte=max_end_date)

        if filling_records:
            fuel_filling_cost_amount = filling_records.filter(liquid_type__in=['diesel', 'gasoline']).aggregate(models.Sum('total_amount'))['total_amount__sum']
            other_filling_cost_amount = filling_records.exclude(liquid_type__in=['diesel', 'gasoline']).aggregate(models.Sum('total_amount'))['total_amount__sum']
            if fuel_filling_cost_amount == None:
                fuel_filling_cost_amount = 0
            if other_filling_cost_amount == None:
                other_filling_cost_amount = 0

        # caculate VehicleDepreciation
        for n in range(int ((max_end_date - min_start_date).days)+1):
            d = min_start_date + timedelta(n)
            vehicle_depreciation_record = VehicleDepreciation.get_vehicle_depreciation(vehicle_instance, d)
            if vehicle_depreciation_record:
                depreciation_amount += vehicle_depreciation_record.depreciation_amount

            # calculate bank interest
            bank_interest_record = VehicleBankInterest.get_vehicle_bank_interest(vehicle_instance, d)
            if bank_interest_record:
                bank_interest_amount += bank_interest_record.interest_amount

        # maintenance_amount
        maintenance_amount = VehicleMaintenanceRepairPart.get_maintenance_amount(vehicle_instance, min_start_date, max_end_date)
        

        total_cost = fuel_filling_cost_amount + other_filling_cost_amount + maintenance_amount + depreciation_amount + bank_interest_amount

        
        monthly_salary_display = ""
        hourly_salary_display = ""
        
        # List driver
        drivers = []
        for record in vehicle_records_with_driver:
            if record.driver not in drivers:
                drivers.append(record.driver)
                
        if len(drivers) == 0:
            monthly_salary_display = "Không có tài xế"
            hourly_salary_display = "Không có tài xế"

        for driver in drivers:

            vehicle_records_per_driver = vehicle_records_with_driver.filter(driver=driver)
            salary_data = calculate_driver_salary(vehicle_records_per_driver, None, select_start_date, select_end_date)
            if salary_data['success'] == 'false':
                monthly_salary = salary_data['message']
                hourly_salary = salary_data['message']
                monthly_salary_display += f'- {driver.full_name}: {monthly_salary}\n'
                hourly_salary_display += f'- {driver.full_name}: {hourly_salary}\n'

            else:
                monthly_salary = salary_data['data']['monthly_salary']['total_monthly_salary']
                hourly_salary = salary_data['data']['hourly_salary']['total_hourly_salary']
                total_cost += monthly_salary + hourly_salary
                monthly_salary = format_money_PL(monthly_salary)
                hourly_salary = format_money_PL(hourly_salary)
                monthly_salary_display += f'- {driver.full_name}: {monthly_salary}\n'
                hourly_salary_display += f'- {driver.full_name}: {hourly_salary}\n'
            
        total_revenue = revenue
        if type(revenue_base) != str:
            revenue_base = format_money_PL(revenue_base)

        if type(revenue) != str:
            revenue = format_money_PL(revenue)
        
        if type(total_revenue) != str: 
            total_profit = format_money_PL(total_revenue - total_cost)
        else:
            total_profit = total_revenue
            

        rows.append({
            "STT": len(rows) + 1,
            "Tên nhận dạng khi mua": vehicle_instance.vehicle_name,
            "Tên GPS": gps_name,
            "Lịch sử đơn giá": revenue_base_display,
            "Số giờ làm": round(total_working_hours, 2),
            "Doanh thu": revenue,
            "Nhiên liệu": format_money_PL(fuel_filling_cost_amount),  
            "Nhớt": format_money_PL(other_filling_cost_amount),  
            "Sửa xe + mua vật tư": format_money_PL(maintenance_amount),
            "Khấu hao xe": format_money_PL(depreciation_amount),
            "Lãi ngân hàng": format_money_PL(bank_interest_amount),
            "Lương cơ bản": monthly_salary_display.strip(),
            "Lương theo giờ": hourly_salary_display.strip(),
            "Tổng chi phí": format_money_PL(total_cost),
            "Lợi nhuận": total_profit,
            "Ghi chú": "",
            "row_id": f"row-{vehicle_instance.pk}"
        })
    else:

        # # only keep records which has driver
        # Quyết định hiển thị toàn bộ xe không lọc tài xế nữa
        # vehicle_operation_records = vehicle_operation_records.filter(driver__isnull=False)
        if not vehicle_operation_records:
            return {"success": "false",
                    "message": "Không tìm thấy dữ liệu trong khoảng thời gian đã chọn",
                    }

        # Get list of unique vehicle together
        unique_gps_vehicles = []
        vehicles = VehicleDetail.objects.filter(vehicle_type__allowed_to_display_in_revenue_table='Cho phép')
        for vehicle in vehicles:
            if vehicle.gps_name not in unique_gps_vehicles:
                unique_gps_vehicles.append(vehicle.gps_name)
        # Sort
        unique_gps_vehicles.sort()
        # if there is "XE CHẤM CÔNG" in unique_values, remove it, and add it to the bottom
        if 'XE CHẤM CÔNG' in unique_gps_vehicles:
            unique_gps_vehicles.remove('XE CHẤM CÔNG')   
            unique_gps_vehicles = unique_gps_vehicles + ['XE CHẤM CÔNG']

        # Don't use vehicle with license plate "72"
        unique_gps_vehicles = [value for value in unique_gps_vehicles if not value.startswith('72')]

        for gps_name in unique_gps_vehicles:
            vehicle_instance = VehicleDetail.objects.get(gps_name=gps_name)
            rows.append({
                "vehicle": vehicle_instance.gps_name,
                "start_date": min_start_date,
                "end_date": max_end_date,
                "row_id": f"row-{vehicle_instance.pk}"
            })

    return {
        'success': 'true',
        'message': 'Tính toán thời gian thành công',
        'rows': rows,
        'headers': rows[0].keys(),
        'update': update
    }


@register.filter(name='calculate_total_payment_state')
def calculate_total_payment_state(maintenance_record):
    if maintenance_record == None:
        return {
            'total_purchase_amount': 0,
            'total_transferred_amount': 0,
            'total_debt_amount': 0
        }
    states = maintenance_record.calculate_all_provider_payment_states()
    # print(states)
    total_purchase_amount = 0
    total_transferred_amount = 0
    total_debt_amount = 0
    for state in states.values():
        total_purchase_amount += state['purchase_amount']
        total_transferred_amount += state['transferred_amount']
        total_debt_amount += state['debt_amount']
        # print(total_purchase_amount)
        # print(total_transferred_amount)
        # print(total_debt_amount)
    return {
        'total_purchase_amount': total_purchase_amount,
        'total_transferred_amount': total_transferred_amount,
        'total_debt_amount': total_debt_amount
    }


@register.filter(name='get_verbose_name')
def get_verbose_name(model_name, field_name):
    try:
        model_class = globals()[model_name]
        return model_class._meta.get_field(field_name).verbose_name
    except Exception:
        return field_name

@register.filter(name='get_field_name_from_verbose')
def get_field_name_from_verbose(model_name, verbose_name):
    try:
        model_class = globals()[model_name]
        for field in model_class._meta.fields:
            if field.verbose_name == verbose_name:
                return field.name
        return verbose_name  # Return the verbose name if no match is found
    except Exception:
        return verbose_name

@register.filter(name='get_project')
def get_project(project_id):
    """
    Get project object from project ID
    """
    try:
        return Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return None
