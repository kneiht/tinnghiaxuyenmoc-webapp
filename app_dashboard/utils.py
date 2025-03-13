
import datetime
from datetime import timedelta

from django.db.models import Q, Sum
from django.utils import timezone

from .forms import *
from .models.models import *

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
        # User
        'Thêm User': 'Thêm tài khoản mới',
        'Tạo User mới': 'Tạo tài khoản mới',
        'Cập nhật User': 'Cập nhật tài khoản',

        'Thêm UserPermission': 'Cấp quyền mới',
        'Tạo UserPermission mới': 'Cấp quyền cho tài khoản',
        'Cập nhật UserPermission': 'Cấp quyền cho tài khoản',

        'title_bar_page_projects': 'Trang quản lý các dự án',
        'Tiêu đề cho trang: page_projects': 'Trang quản lý các dự án',

        'Thêm Project': 'Thêm dự án',
        'Tạo Project mới': 'Tạo dự án',
        'Cập nhật Project': 'Cập nhật dự án',
        
        # UserExtra
        'Thêm UserExtra': 'Thêm dữ liệu mới',
        'Tạo UserExtra mới': 'Tạo thông tin tài khoản bổ sung',
        'Cập nhật UserExtra': 'Cập nhật thông tin tài khoản bổ sung',

        # Task
        'Thêm Task': 'Thêm dữ liệu mới',
        'Tạo Task mới': 'Tạo nhiệm vụ',
        'Cập nhật Task': 'Cập nhật nhiệm vụ',

        # TaskUser
        'Thêm TaskUser': 'Thêm dữ liệu mới',
        'Tạo TaskUser mới': 'Tạo người dùng nhiệm vụ',
        'Cập nhật TaskUser': 'Cập nhật người dùng nhiệm vụ',

        # ProjectUser
        'Thêm ProjectUser': 'Thêm dữ liệu mới',
        'Tạo ProjectUser mới': 'Tạo nhân sự dự án',
        'Cập nhật ProjectUser': 'Cập nhật nhân sự dự án',

        # Job
        'Thêm Job': 'Thêm CV',
        'Tạo Job mới': 'Tạo công việc',
        'Cập nhật Job': 'Cập nhật công việc',

        # JobPlan
        'Thêm JobPlan': 'Thêm dữ liệu mới',
        'Tạo JobPlan mới': 'Tạo kế hoạch CV mới',
        'Cập nhật JobPlan': 'Cập nhật kế hoạch CV',

        # JobDateReport
        'Thêm JobDateReport': 'Thêm dữ liệu mới',
        'Tạo JobDateReport mới': 'Tạo báo cáo ngày',
        'Cập nhật JobDateReport': 'Cập nhật báo cáo ngày',

        # VehicleType
        'Thêm VehicleType': 'Thêm dữ liệu mới',
        'Tạo VehicleType mới': 'Tạo loại xe',
        'Cập nhật VehicleType': 'Cập nhật loại xe',

        # StaffData
        'Thêm StaffData': 'Thêm dữ liệu mới',
        'Tạo StaffData mới': 'Tạo dữ liệu nhân viên',
        'Cập nhật StaffData': 'Cập nhật dữ liệu nhân viên',

        # VehicleRevenueInputs
        'Thêm VehicleRevenueInputs': 'Thêm dữ liệu mới',
        'Tạo VehicleRevenueInputs mới': 'Tạo dữ liệu tính doanh thu xe',
        'Cập nhật VehicleRevenueInputs': 'Cập nhật dữ liệu doanh thu xe',

        # DriverSalaryInputs
        'Thêm DriverSalaryInputs': 'Thêm dữ liệu mới',
        'Tạo DriverSalaryInputs mới': 'Tạo dữ liệu tính lương tài xế',
        'Cập nhật DriverSalaryInputs': 'Cập nhật dữ liệu lương tài xế',

        # VehicleDetail
        'Thêm VehicleDetail': 'Thêm dữ liệu mới',
        'Tạo VehicleDetail mới': 'Tạo dữ liệu xe chi tiết',
        'Cập nhật VehicleDetail': 'Cập nhật dữ liệu xe chi tiết',

        # DumbTruckPayRate
        'Thêm DumbTruckPayRate': 'Thêm dữ liệu mới',
        'Tạo DumbTruckPayRate mới': 'Tạo dữ liệu lương xe ben',
        'Cập nhật DumbTruckPayRate': 'Cập nhật dữ liệu lương xe ben',

        # DumbTruckRevenueData
        'Thêm DumbTruckRevenueData': 'Thêm dữ liệu mới',
        'Tạo DumbTruckRevenueData mới': 'Tạo dữ liệu doanh thu xe ben',
        'Cập nhật DumbTruckRevenueData': 'Cập nhật dữ liệu doanh thu xe ben',

        # Location
        'Thêm Location': 'Thêm dữ liệu mới',
        'Tạo Location mới': 'Tạo địa điểm',
        'Cập nhật Location': 'Cập nhật địa điểm',

        # NormalWorkingTime
        'Thêm NormalWorkingTime': 'Thêm dữ liệu mới',
        'Tạo NormalWorkingTime mới': 'Tạo thời gian làm việc',
        'Cập nhật NormalWorkingTime': 'Cập nhật thời gian làm việc',

        # Holiday
        'Thêm Holiday': 'Thêm dữ liệu mới',
        'Tạo Holiday mới': 'Tạo ngày lễ',
        'Cập nhật Holiday': 'Cập nhật ngày lễ',

        # VehicleOperationRecord
        'Thêm VehicleOperationRecord': 'Thêm dữ liệu mới',
        'Tạo VehicleOperationRecord mới': 'Tạo dữ liệu vận hành xe',
        'Cập nhật VehicleOperationRecord': 'Cập nhật dữ liệu vận hành xe',

        # FuelFillingRecord
        'Thêm FuelFillingRecord': 'Thêm dữ liệu mới',
        'Tạo FuelFillingRecord mới': 'Tạo phiếu đổ xăng',
        'Cập nhật FuelFillingRecord': 'Cập nhật phiếu đổ xăng',

        # LubeFillingRecord
        'Thêm LubeFillingRecord': 'Thêm dữ liệu mới',
        'Tạo LubeFillingRecord mới': 'Tạo phiếu đổ nhớt',
        'Cập nhật LubeFillingRecord': 'Cập nhật phiếu đổ nhớt',

        # VehicleDepreciation
        'Thêm VehicleDepreciation': 'Thêm dữ liệu mới',
        'Tạo VehicleDepreciation mới': 'Tạo khấu hao xe',
        'Cập nhật VehicleDepreciation': 'Cập nhật khấu hao xe',

        # VehicleBankInterest
        'Thêm VehicleBankInterest': 'Thêm dữ liệu mới',
        'Tạo VehicleBankInterest mới': 'Tạo lãi suất ngân hàng',
        'Cập nhật VehicleBankInterest': 'Cập nhật lãi suất ngân hàng',

        # VehicleMaintenance
        'Thêm VehicleMaintenance': 'Thêm dữ liệu mới',
        'Tạo VehicleMaintenance mới': 'Tạo phiếu sửa chữa',
        'Cập nhật VehicleMaintenance': 'Phiếu sửa chữa',

        # RepairPart
        'Thêm RepairPart': 'Thêm dữ liệu mới',
        'Tạo RepairPart mới': 'Tạo phụ tùng sửa chữa',
        'Cập nhật RepairPart': 'Cập nhật phụ tùng sửa chữa',
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
        if 'check_month' not in query_params:
            check_month = kwargs.get('check_month', '')
        else:
            check_month = query_params['check_month'][0]
        

        if check_month != '':
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

        # filter records which has start time 
        records = records.filter(start_time__date__range=[start_date, end_date])


    
    # Determine the fields to be used as filter options based on the selected page
    fields = [field.name for field in model_class._meta.get_fields() if 
                  isinstance(field, (models.CharField, models.TextField))]

    # Add fields from forein keys
    for field in model_class._meta.get_fields():
        if isinstance(field, models.ForeignKey):
            # iterate all fields in foreign key,check if it is a CharField or TextField
            for foreign_field in field.related_model._meta.get_fields():
                if isinstance(foreign_field, (models.CharField, models.TextField)):
                    fields.append(f"{field.name}__{foreign_field.name}")




    # Construct Q objects for filtering
    combined_query = Q()
    if 'all' in query_params:
        specified_fields = fields
        all_fields_query = Q()
        for value in query_params['all']:
            if value == '':
                continue
            for specified_field in specified_fields:
                all_fields_query |= Q(**{f"{specified_field}__icontains": value})
        combined_query &= all_fields_query
        
    else:
        for field, values in query_params.items():
            if field in fields:
                try:
                    model_class._meta.get_field(field)
                    field_query = Q()
                    for value in values:
                        if value == '':
                            continue
                        field_query |= Q(**{f"{field}__icontains": value})
                    combined_query &= field_query
                except FieldDoesNotExist:
                    print(f"Ignoring invalid field: {field}")
    # Filter records based on the query
    records_filtered = records.filter(combined_query)



    # Fix bug no records when searching driver because driver must be searched in full_name
    if model_class == VehicleOperationRecord:
        driver_name = request.GET.get('all', [''])
        records_have_driver = records.filter(driver__full_name__icontains=driver_name)
        records = records_filtered | records_have_driver
    else:
        records = records_filtered

    if request.GET.get('sort'):
        records = records.order_by(request.GET.get('sort'))
            
    return records

