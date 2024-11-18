
import datetime
from datetime import timedelta

from django.db.models import Q, Sum
from django.utils import timezone

from .forms import *
from .models import *

# AUTHENTICATION =============================================================
def is_admin(user):
    return user.is_authenticated and user.is_active and user.is_staff and user.is_superuser

def get_start_end_of_the_month(month, year):
    # Start of the month
    start_date_of_month = datetime(year, month, 1)
    # Calculate the end of the month by moving to the next month and subtracting one day
    if month == 12:
        end_date_of_month = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date_of_month = datetime(year, month + 1, 1) - timedelta(days=1)
    return start_date_of_month.date(), end_date_of_month.date()

import base64, json
def encode_base64(input_string):
    # Convert the string to bytes
    byte_string = input_string.encode('utf-8')
    # Encode to Base64
    base64_bytes = base64.b64encode(byte_string)
    # Convert Base64 bytes back to a string
    base64_string = base64_bytes.decode('utf-8')
    return base64_string

def get_valid_date(date):
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    except:
        date = timezone.now().date()
    date = date.strftime('%Y-%m-%d')
    return date

def get_valid_month(date):
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    except:
        try:
            date = datetime.strptime(date, '%Y-%m').date()
        except:
            date = timezone.now().date()
    month = date.strftime('%Y-%m')
    return month


def get_valid_id(id):
    try:
        id = int(id)
    except:
        id = 0
    return id




def get_valid_int(value):
    try:
        value = int(value)
    except:
        value = 0
    return value


import base64, json
def decode_params(encoded_params):
    # Convert string back to bytes
    byte_string = encoded_params.encode('utf-8')
    # Base64 decode the byte string
    decoded_bytes = base64.b64decode(byte_string)
    # Convert bytes back to string
    return decoded_bytes.decode('utf-8')



def translate(text):
    translated_text = {
        'title_bar_page_projects': 'Trang quản lý các dự án',
        'Tiêu đề cho trang: page_projects': 'Trang quản lý các dự án',
        'Thêm Project': 'Thêm dự án',
        'Thêm Job': 'Thêm CV',
        'Tạo Project mới': 'Tạo dự án mới',
        'Cập nhật Project': 'Cập nhật dự án'
    }

    if text not in translated_text:
        return text
    else:
        return translated_text[text]






def progress_by_time(record, check_date=None):
    if not check_date or check_date == 'None':
        check_date = timezone.now().date()
    else:
        if type(check_date) == str:
            check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
    # print('>>>>>>>>>>>>>>>>>>>> progress_by_time', check_date, type(check_date))

    duration = (record.end_date - record.start_date).days + 1
    if duration == 0:
        progress = 1
        percent = 100
    else:
        progress = int((check_date - record.start_date).days) + 1
        percent = int((progress / duration) * 100) if progress<=duration else 100

    if progress <= 0:
        return {
            'progress': 0,
            'status': 'not_started',
            'duration': duration,
            'percent': 0,
        }


    # Check if the record is jobplan
    if record.__class__.__name__ == 'JobPlan':
        record.status = record.job.status

    if record.status == 'done':
        status = 'green'
    elif record.status == 'in_progress':
        if percent < 100:
            status = 'blue'
        else:
            status = 'red'
    else:
        status = 'gray'

    return {
        'progress': progress,
        'duration': duration,
        'percent': percent,
        'status': status
    }

def progress_by_quantity(record, check_date=None):
    if not check_date or check_date == 'None':
        check_date = timezone.now().date()
    else:
        if type(check_date) == str:
            check_date = datetime.strptime(check_date, '%Y-%m-%d').date()

    if record.__class__.__name__ == 'Project':
        # Caculate all the quantity of jobs in the project
        total_quantity = record.job_set.aggregate(Sum('quantity'))['quantity__sum'] or 0
        
        # Calculate the quantity of all job reports
        job_date_reports = JobDateReport.objects.filter(job__project=record)
        total_quantity_reported = job_date_reports.aggregate(Sum('quantity'))['quantity__sum'] or 0

    elif record.__class__.__name__ == 'Job':
        total_quantity = record.quantity
        job_date_reports = JobDateReport.objects.filter(job=record, date__lte=check_date)
        total_quantity_reported = job_date_reports.aggregate(Sum('quantity'))['quantity__sum'] or 0

    elif record.__class__.__name__ == 'JobPlan':
        total_quantity = record.plan_quantity
        job_date_reports = JobDateReport.objects.filter(job=record.job, date__gte=record.start_date, date__lte=check_date)
        total_quantity_reported = job_date_reports.aggregate(Sum('quantity'))['quantity__sum'] or 0

        
    if total_quantity == 0:
        percent = 0
    else:
        percent = min(int((total_quantity_reported / total_quantity) * 100), 100)


    if record.status == 'done':
        status = 'green'
    elif record.status == 'in_progress':
        status = 'blue'
    else:
        status = 'gray'

    return {
        'total_quantity': total_quantity,
        'total_quantity_reported': total_quantity_reported,
        'percent': percent,
        'status': status
    }





def progress_by_amount(record, check_date=None):
    if not check_date or check_date == 'None':
        check_date = timezone.now().date()
    else:
        if type(check_date) == str:
            check_date = datetime.strptime(check_date, '%Y-%m-%d').date()

    if record.__class__.__name__ == 'Project':
        # Caculate all the total_amount of jobs in the project
        total_amount = record.job_set.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Calculate the amount of all job reports
        job_date_reports = JobDateReport.objects.filter(job__project=record, date__lte=check_date)
        total_amount_reported = job_date_reports.aggregate(Sum('date_amount'))['date_amount__sum'] or 0

    elif record.__class__.__name__ == 'Job':
        total_amount = record.total_amount
        job_date_reports = JobDateReport.objects.filter(job=record, date__lte=check_date)
        total_amount_reported = job_date_reports.aggregate(Sum('date_amount'))['date_amount__sum'] or 0

    elif record.__class__.__name__ == 'JobPlan':
        total_amount = record.plan_amount
        job_date_reports = JobDateReport.objects.filter(job=record.job, date__gte=record.start_date, date__lte=check_date)
        total_amount_reported = job_date_reports.aggregate(Sum('date_amount'))['date_amount__sum'] or 0

        
    if total_amount == 0:
        percent = 0
    else:
        percent = min(int((total_amount_reported / total_amount) * 100), 100)


    if record.status == 'done':
        status = 'green'
    elif record.status == 'in_progress':
        status = 'blue'
    else:
        status = 'gray'

    return {
        'total_amount': int(total_amount),
        'total_amount_reported': int(total_amount_reported),
        'percent': percent,
        'status': status
    }




def progress_by_plan(record, check_date = None):
    if not check_date or check_date == 'None':
        check_date = timezone.now().date()
    else:
        if type(check_date) == str:
            check_date = datetime.strptime(check_date, '%Y-%m-%d').date()

    if record.__class__.__name__ != 'Project':
        return None

    # Get jobs in the project
    jobs = Job.objects.filter(project_id=record.id)
    planned_amount_to_now_project = 0
    project_amount = 0
    for job in jobs:
        project_amount += job.total_amount
        duration_job = (job.end_date - job.start_date).days + 1
        days_to_now_job = (check_date - job.start_date).days + 1
        # Skip if the job is not started
        if days_to_now_job < 0:
            continue

        # Caculate planned amount
        planned_amount_to_now_job = int((days_to_now_job / duration_job) * job.total_amount)
        if planned_amount_to_now_job >= job.total_amount:
            planned_amount_to_now_job = job.total_amount
        planned_amount_to_now_project += planned_amount_to_now_job
        
    
    if project_amount == 0:
        return None
    percent = int((planned_amount_to_now_project / project_amount) * 100)


    res = {
        'planned_amount_to_now_project': int(planned_amount_to_now_project),
        'total_amount': int(project_amount),
        'percent': percent
    }
    return res









def filter_records(request, records, model_class, **kwargs):
    # Get all query parameters except 'sort' as they are assumed to be field filters
    query_params = {k: v for k, v in request.GET.lists() if k != 'sort'} 
    if model_class == VehicleOperationRecord:

        check_month = kwargs.get('start_date', '')
        if check_month != '':
            check_month = get_valid_month(check_month)
            year, month = check_month.split('-')
            start_date, end_date = get_start_end_of_the_month(int(month), int(year))
        else:
            # Add start_date and end_date form params to query_params if they are not present
            if 'start_date' not in query_params:
                start_date = get_valid_date(kwargs.get('start_date', ''))
            else:
                start_date = query_params['start_date'][0]


            if 'end_date' not in query_params:
                end_date = get_valid_date(kwargs.get('end_date', ''))
            else:
                end_date = query_params['end_date'][0]
        # print('>>>> start date and end date:',start_date, end_date)

        # filter records which has start time 
        records = records.filter(start_time__date__range=[start_date, end_date])



    # Determine the fields to be used as filter options based on the selected page
    if model_class == Project:
        fields = ['all', 'name', 'description']
    elif model_class == Job:
        fields = ['all', 'name', 'status', 'category', 'unit', 'quantity', 'description']
    elif model_class == StaffData:
        fields = ['all', 'full_name', 'identity_card']
    elif model_class == VehicleOperationRecord:
        fields = ['all']
    else:
        # Get all fields except foreign key fields
        fields = [field.name for field in model_class._meta.get_fields() if not isinstance(field, models.ForeignKey)]
        fields.append('all')

    if not query_params:
        # Filter Discontinued and Archived
        if hasattr(model_class, 'status'):
            records = records.exclude(status__in=['archived'])
            
    else:
        # Construct Q objects for filtering
        combined_query = Q()
        if 'all' in query_params:
            specified_fields = fields[1:]  # Exclude 'all' to get the specified fields
            all_fields_query = Q()
            for value in query_params['all']:
                for specified_field in specified_fields:
                    if specified_field in [field.name for field in model_class._meta.get_fields()]:
                        all_fields_query |= Q(**{f"{specified_field}__icontains": value})
            combined_query &= all_fields_query
            
        else:
            for field, values in query_params.items():
                if field in fields:
                    try:
                        model_class._meta.get_field(field)
                        field_query = Q()
                        for value in values:
                            field_query |= Q(**{f"{field}__icontains": value})
                        combined_query &= field_query
                    except FieldDoesNotExist:
                        print(f"Ignoring invalid field: {field}")
        # Filter records based on the query
        records = records.filter(combined_query)
    
    
    if request.GET.get('sort'):
        records = records.order_by(request.GET.get('sort'))
            
    return records

