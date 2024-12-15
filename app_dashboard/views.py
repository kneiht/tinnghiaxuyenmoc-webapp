# security issues
# https://chat.openai.com/share/16295269-0f56-4c6a-8cd7-7ea903fdaf86
# cần check truy cập trang cần đúng school_id and user

import requests, json
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup   

from core import settings
import pandas as pd
from django.views.decorators.csrf import csrf_exempt

import json
import os
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from .forms import *
from .models import *

from .renders import *
from .utils import *

from core.settings import DOMAIN
from django.utils import timezone
from django.urls import reverse_lazy


@login_required
def decide_permission(request, action, params):
    # CHECK PERMISSIONS
    tab = params.get('tab', None)
    if not tab:
        model = params.get('model', None)
        sub_page = model
    elif tab=='vehicle_operation_data_by_date':
        sub_page = 'VehicleOperationRecord'
    elif tab=='driver_salary':
        sub_page = 'ConstructionDriverSalary'
    elif tab=='vehicle_revenue':
        sub_page = 'ConstructionReportPL'

    # FEATURES THAT ARE DEVELOPING
    if sub_page in ("Task", "Announcement"):
        message = 'Không tìm thấy chức năng này. \n Có thể chức năng này đang được phát triển!'
        return render(request, 'components/message_page.html', {'message': message})

    user = request.user
    permission = user.check_permission(sub_page)
    if action == 'read':
        if not permission.read:
            message = 'Bạn chưa được cấp quyền truy cập trang này. \n Vui lòng liên hệ admin cấp quyền.'
            return render(request, 'components/message_page.html', {'message': message})
        else:
            return None
    elif action == 'create':
        if not permission.create:
            message = 'Tạo dữ liệu không thành công vì chưa được cấp quyền. \n\n Vui lòng liên hệ admin cấp quyền.'
            message_type = 'red'
            return render_message(request, message=message, message_type=message_type)
        else:
            return None
    elif action == 'update':
        if not permission.update:
            message = 'Cập nhật dữ liệu không thành công vì chưa được cấp quyền. \n\n Vui lòng liên hệ admin cấp quyền.'
            message_type = 'red'
            return render_message(request, message=message, message_type=message_type)
        else:
            return None

    elif action == 'delete':
        if not permission.delete:
            message = 'Không thể xóa dữ liệu vì chưa được cấp quyền. \n\n Vui lòng liên hệ admin cấp quyền.'
            message_type = 'red'
            return render_message(request, message=message, message_type=message_type)
        else:
            return None
    else:
        return None

# HANDLE FORMS ===============================================================
@login_required
def handle_form(request, model, pk=0):

    # Todo: should have list of model that can be accessed
    # Convert model name to model class
    model_class = globals()[model]
    form_class = globals()[model + 'Form']
    
    # check if not Post => return 404
    if request.method != 'POST':
        return HttpResponseForbidden()
    
    # project_id
    project_id = get_valid_id(request.POST.get('project', 0))
    # Get form
    instance = model_class.objects.filter(pk=pk).first()
    form = form_class(request.POST, request.FILES, instance=instance)

    if form.is_valid():
        instance_form = form.save(commit=False)
        if instance is None:  # This is a new form
            # Handle the case of the project is created and need to be assigned to a user
            # instance_form.user = request.user
            # CHECK PERMISSIONS
            forbit_html = decide_permission(request, 'create', {'model': model})
            if forbit_html:
                return HttpResponse(forbit_html)
        else: # update
            # CHECK PERMISSIONS
            forbit_html = decide_permission(request, 'update', {'model': model})
            if forbit_html:
                return HttpResponse(forbit_html)
        
        instance_form.save()
        if model == 'VehicleMaintenance':
            vehicle_maintenance = instance_form
            # get the list of vehicle_parts VehicleMaintenanceRepairPart
            vehicle_parts = VehicleMaintenanceRepairPart.objects.filter(vehicle_maintenance=vehicle_maintenance)
            vehicle_part_post_ids = request.POST.getlist('vehicle_part_id')
            # check if the id is in the list, if not delete it
            for vehicle_part in vehicle_parts:
                if str(vehicle_part.id) not in vehicle_part_post_ids:
                    vehicle_part.delete()

            parts = request.POST.getlist('part')
            quantities = request.POST.getlist('quantity')
            for part, quantity in zip(parts, quantities):
                if part == '' and quantity == '':
                    continue
                VehicleMaintenanceRepairPart.objects.create(
                    vehicle_maintenance=vehicle_maintenance,
                    repair_part_id=part,
                    quantity=quantity,
                )
        # Save the many to many field, if any
        # form.save_m2m()
        record = instance_form
        record.style = 'just-updated'
        html_message = render_message(request, message='Cập nhật thành công')
        html_record = render_display_records(request, model=model, records=[record], update='True', project_id=project_id)
        return HttpResponse(html_message + html_record)
    else:
        print(form.errors)
        html_modal = render_form(request, model=model, pk=pk, form=form, project_id=project_id)
        return  HttpResponse(html_modal)

@login_required
def get_gantt_chart_data(request, project_id):
    # Get project
    project = get_object_or_404(Project, pk=project_id)
    jobs = project.job_set.all()

    # Sort
    jobs = filter_records(request, jobs, Job)

    # Get checkdate from params
    check_date = request.GET.get('check_date')

    
    # Return json data including job names, start and end dates
    data = []
    for job in jobs:
        data.append({
            'id': job.secondary_id,
            'name': job.name,
            'start': job.start_date.isoformat(),
            'end': job.end_date.isoformat(),
            'progress_time': progress_by_time(job, check_date=check_date)['percent'],
            'progress_amount': progress_by_amount(job, check_date=check_date)['percent'],
        })

    return JsonResponse(data, safe=False)



@login_required
def load_elements(request):
    encoded_params = request.GET.get('q', '')
    params = json.loads(decode_params(encoded_params))
    for key, value in request.GET.items():
        if key != 'q':
            params[key] = value
    print('\n>>>>>>>>>> elements params:', params)
    html = '<div id="load-elements" class"hidden"></div>'

    # CHECK PERMISSIONS
    forbit_html = decide_permission(request, 'read', params)
    if forbit_html:
        return HttpResponse(forbit_html)

    # RENDER ELEMENTS
    elements = params.get('elements', '')
    for element in elements.split('|'):
        element = element.strip()
        if element == 'title_bar':
            html_title_bar = render_title_bar(request, **params)
            html += html_title_bar
        elif element == 'tool_bar':
            html_tool_bar = render_tool_bar(request, **params)
            html += html_tool_bar
        elif element == 'infor_bar':
            html_infor_bar = render_infor_bar(request, **params)
            html += html_infor_bar
        elif element == 'display_records':
            html_display_records = render_display_records(request, **params)
            html += html_display_records
        elif element == 'message':
            html_message = render_message(request, **params)
            html += html_message
        elif element == 'modal_form':
            html_modal_form = render_form(request, **params)
            html += html_modal_form
        elif element == 'gantt_chart':
            pass
        elif element == 'weekplan_table':
            html_weekplan_table = render_weekplan_table(request, **params)

    return HttpResponse(html)




@login_required
def load_weekplan_table(request, project_id):
    check_date = request.GET.get('check_date')
    html_weekplan_table = render_weekplan_table(request, project_id, check_date)
    html_tool_bar = '<div id="tool-bar" class="hidden"></div>'
    return HttpResponse(html_weekplan_table + html_tool_bar)

@login_required
def handle_weekplan_form(request):
    if request.method != 'POST':
        return HttpResponseForbidden()
    form = request.POST

    try:
        start_date = form.get('start_date')
        end_date = form.get('end_date')
        check_date = form.get('check_date')
        project_id = form.get('project_id')
        project = Project.objects.get(pk=project_id)


        # get all jobs of the project
        jobs = Job.objects.filter(project_id=project_id)

        weekplan_status = form.get('weekplan_status')
        user_role = ProjectUser.objects.filter(project=project, user=request.user).first() 

        if user_role.role == 'technician' or user_role.role == 'all':
            message = "Phê duyệt thành công"
            for job in jobs:
                jobplan = JobPlan.objects.filter(job=job, start_date=start_date, end_date=end_date).first()
                if jobplan:
                    jobplan.status = weekplan_status
                    jobplan.save()

        elif user_role.role == 'supervisor' or user_role.role == 'all':
            message = "Cập nhật kế hoạch tuần thành công. \n\nĐã chuyển kế hoạch đến người xét duyệt!"
            weekplan_status = 'wait_for_approval'
            for job in jobs:
                note = form.get(f'note_{job.pk}')
                quantity = form.get(f'plan_quantity_{job.pk}')
                try:
                    quantity = float(quantity)
                except ValueError as e:
                    quantity = 0

                if type(note) != str: note = ''

                if quantity > job.quantity:
                    message = f'Lỗi khi nhập khối lượng kế hoạch cho công việc "{job.name}". Khối lượng kế hoạch phải nhỏ hơn khối lượng công việc ({str(job.quantity)}).'
                    html_message = render_message(request, message=message, message_type='red')
                    return HttpResponse(html_message)
                
                jobplan = JobPlan.objects.filter(job=job, start_date=start_date, end_date=end_date).first()
                if quantity == 0 and note.strip() == '':
                    if jobplan:
                        jobplan.delete()
                        pass
                    continue

                if jobplan:
                    jobplan.note = note
                    jobplan.plan_quantity = quantity
                    jobplan.status = weekplan_status
                    jobplan.save()
                    continue
                else:
                    JobPlan(
                        job=job,
                        start_date=start_date,
                        end_date=end_date,
                        plan_quantity=quantity,
                        note=note,
                        status=weekplan_status
                    ).save()
            
        
        html_weekplan_table = render_weekplan_table(request, project_id, check_date=check_date)
        html_infor_bar = render_infor_bar(request, page = 'page_each_project', project_id=project_id, check_date=check_date)
        html_message = render_message(request, message=message)
        return HttpResponse(html_message + html_weekplan_table + html_infor_bar)

    except Exception as e:
        raise e
        html = render_message(request, message='Có lỗi: ' + str(e), message_type='red')
        return HttpResponse(html)
        

@login_required
def handle_date_report_form(request):
    if request.method != 'POST':
        return HttpResponseForbidden()
    
    form = request.POST
    check_date = form.get('check_date')
    try:
        check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
    except:
        check_date = timezone.now().date()
    # Get monday and sunday dates of the week that contains check_date
    monday = check_date - timedelta(days=check_date.weekday())
    sunday = check_date + timedelta(days=6 - check_date.weekday())
    try:
        check_date = form.get('check_date')
        project_id = form.get('project_id')
        # get all jobs of the project
        jobs = Job.objects.filter(project_id=project_id)

        has_jobplan = False
        for job in jobs:
            jobplan_in_week = JobPlan.objects.filter(start_date__gte=monday, end_date__lte=sunday, job=job).first()
            if jobplan_in_week:
                if jobplan_in_week.status == 'wait_for_approval':
                    html = render_message(request, message='Không cập nhật được báo cáo ngày.\n\nVui lòng chờ báo cáo tuần được phê duyệt trước.', message_type='red')
                    return HttpResponse(html)
                elif jobplan_in_week.status == 'rejected':
                    html = render_message(request, message='Không cập nhật được báo cáo ngày.\n\nBáo cáo tuần đã bị từ chối, vui lòng cập nhật lại báo cáo tuần.', message_type='red')
                    return HttpResponse(html)
                elif jobplan_in_week.status == 'approved':
                    has_jobplan = True
        if not has_jobplan:
            html = render_message(request, message='Không cập nhật được báo cáo ngày.\n\nChưa tạo báo cáo tuần.', message_type='red')
            return HttpResponse(html)


        for job in jobs:
            note = form.get(f'date_note_{job.pk}')
            quantity = form.get(f'date_quantity_{job.pk}')
            material = form.get(f'date_material_{job.pk}')
            labor = form.get(f'date_labor_{job.pk}')
            try:
                quantity = float(quantity)
            except:
                quantity = 0

            if type(note) != str: note = ''
            if type(material) != str: material = ''
            if type(labor) != str: labor = ''

            job_date_report = JobDateReport.objects.filter(job=job, date=check_date).first()

            current_date_quantity = job_date_report.quantity if job_date_report else 0

            total_quantity_reported = progress_by_quantity(job)['total_quantity_reported'] - current_date_quantity
            total_quantity_left = job.quantity - total_quantity_reported
            
            if int(quantity) > total_quantity_left:
                message = f'Lỗi khi nhập khối lượng hoàn thành (đang nhập {quantity}) trong ngày cho công việc "{job.name}". Khối lượng hoàn thành phải nhỏ hơn khối lượng còn lại ({str(total_quantity_left)}).'
                html_message = render_message(request, message=message, message_type='red')
                return HttpResponse(html_message)


            if quantity == 0 and note.strip() == '' and material.strip() == '' and labor.strip() == '':
                if job_date_report:
                    job_date_report.delete()
                continue


            if job_date_report:
                job_date_report.note = note
                job_date_report.quantity = quantity
                job_date_report.material = material
                job_date_report.labor = labor
                job_date_report.save()
                continue
            else:
                JobDateReport(
                    job=job,
                    date=check_date,
                    quantity=quantity,
                    material=material,
                    labor=labor,
                    note=note
                ).save()

        html_weekplan_table = render_weekplan_table(request, project_id, check_date=check_date)
        html_message = render_message(request, message='Cập nhật báo cáo thành công')
        html_infor_bar = render_infor_bar(request, page = 'page_each_project', project_id=project_id, check_date=check_date)
        return HttpResponse(html_message + html_weekplan_table + html_infor_bar) 
    
    except Exception as e:
        raise e
        html = render_message(request, message='Có lỗi: ' + str(e), message_type='red')
        return HttpResponse(html)
        


def handle_vehicle_operation_form(request):
    def convert_time(time_str, time_sign):
        hours, minutes, seconds = map(int, time_str.split(":"))
        total_seconds = hours * 3600 + minutes * 60 + seconds
        duration_seconds = total_seconds
        if time_sign == 'minus':
            duration_seconds = -duration_seconds
        return duration_seconds
    
    if request.method != 'POST':
        return HttpResponseForbidden()
    
    try:
        form = request.POST
        # Get list of ids   
        ids = form.getlist('id')
        for id in ids:
            driver = StaffData.objects.filter(pk=get_valid_id(form.get(f'driver_{id}', None))).first()
            location = Location.objects.filter(pk=get_valid_id(form.get(f'location_{id}', None))).first()
            record = VehicleOperationRecord.objects.get(pk=id)
            record.driver = driver
            record.location = location
            record.fuel_allowance = form.get(f'fuel_allowance_{id}', None)
            record.note = form.get(f'note_{id}', None)
            record.allow_overtime = False if not form.get(f'allow_overtime_{id}', False) else True
            if record.source == 'manual':
                try:
                    # duration seconds
                    duration_seconds_str = form.get(f'duration_seconds_{id}', None)
                    duration_seconds_sign = form.get(f'duration_seconds_sign_{id}', None)
                    duration_seconds = convert_time(duration_seconds_str, duration_seconds_sign)
                    record.duration_seconds = duration_seconds
                    # over time
                    overtime_str = form.get(f'overtime_{id}', None)
                    overtime_sign = form.get(f'overtime_sign_{id}', None)
                    overtime = convert_time(overtime_str, overtime_sign)
                    record.overtime = overtime
                    # normal_woring_time
                    normal_working_time_str = form.get(f'normal_working_time_{id}', None)
                    normal_working_time_sign = form.get(f'normal_working_time_sign_{id}', None)
                    normal_working_time = convert_time(normal_working_time_str, normal_working_time_sign)
                    record.normal_working_time = normal_working_time
                except:
                    raise e
                
                if not driver:
                    # remove record
                    record.delete()
                    continue
            record.save()
            
        # Add new records
        new_index = 0
        while True:
            new_index += 1
            if not form.get(f'vehicle_new_{new_index}', None):
                break

            vehicle_new = form.get(f'vehicle_new_{new_index}', None)
            start_time_new = form.get(f'start_time_new_{new_index}', None)
            driver_new = form.get(f'driver_new_{new_index}', None)
            location_new = form.get(f'location_new_{new_index}', None)
            duration_seconds_new = form.get(f'duration_seconds_new_{new_index}', None)
            duration_seconds_sign_new = form.get(f'duration_seconds_sign_new_{new_index}', None)
            overtime_new = form.get(f'overtime_new_{new_index}', None)
            overtime_sign_new = form.get(f'overtime_sign_new_{new_index}', None)
            normal_working_time_new = form.get(f'normal_working_time_new_{new_index}', None)
            normal_working_time_sign_new = form.get(f'normal_working_time_sign_new_{new_index}', None)
            fuel_allowance_new = form.get(f'fuel_allowance_new_{new_index}', None)
            note_new = form.get(f'note_new_{new_index}', None)
            allow_overtime_new = False if not form.get(f'allow_overtime_new_{new_index}', False) else True
            try:
                # duration seconds
                duration_seconds_str = duration_seconds_new
                duration_seconds_sign = duration_seconds_sign_new
                duration_seconds = convert_time(duration_seconds_str, duration_seconds_sign)

                # over time
                overtime_str = overtime_new
                overtime_sign = overtime_sign_new
                overtime = convert_time(overtime_str, overtime_sign)

                # normal_woring_time
                normal_working_time_str = normal_working_time_new
                normal_working_time_sign = normal_working_time_sign_new
                normal_working_time = convert_time(normal_working_time_str, normal_working_time_sign)

            except Exception as e:
                raise e
        
            vehicle = vehicle_new   
            driver = StaffData.objects.filter(pk=get_valid_id(driver_new)).first()
            location = Location.objects.filter(pk=get_valid_id(location_new)).first()
            
            start_time = start_time_new
            # convert start time to datetime object
            start_time = datetime.strptime(start_time, '%d/%m/%Y')
            end_time = start_time
            fuel_allowance = get_valid_int(fuel_allowance_new)
            note = note_new
            allow_overtime = allow_overtime_new

            if not driver:
                continue

            new_record = VehicleOperationRecord.objects.create(
                vehicle=vehicle,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration_seconds,
                overtime=overtime,
                normal_working_time=normal_working_time,
                fuel_allowance=fuel_allowance,
                note=note,
                source='manual',
                driver=driver,
                location=location,
                allow_overtime=allow_overtime
            )
            ids.append(new_record.id)

        # Get records by ids
        group_by = form.get('group_by')
        tab = form.get('tab')
        records = VehicleOperationRecord.objects.filter(pk__in=ids).order_by('source', 'start_time')
        
        # Get start_date from start_time
        
        start_date = records.first().start_time.date()
        end_date = records.last().end_time.date()
        html_display = render_display_records(request, model='VehicleOperationRecord', 
            start_date=start_date, end_date=end_date, records=records, group_by=group_by, tab=tab, update=True)

        html_message = render_message(request, message='Cập nhật thành công!\n\nLưu ý các dòng nhập tay nếu không có TÀI XẾ sẽ bị xóa', message_type='green')
        html = html_message + html_display
        return HttpResponse(html)
    except Exception as e:
        html = render_message(request, message='Có lỗi: ' + str(e), message_type='red') 
        return HttpResponse(html)


@login_required
def download_excel_template(request, template_name):
    # Get the Excel file from media/excel/Mẫu công việc trong dự án.xlsx
    excel_file = os.path.join(settings.MEDIA_ROOT, 'excel', f'cong-viec-trong-du-an.xlsx')

    # Return the file
    with open(excel_file, 'rb') as f:
        excel_data = f.read()

    response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="cong-viec-trong-du-an.xlsx"'
    return response


@login_required
def upload_project(request, project_id):
    if request.method != 'POST':
        return "API này chỉ dùng POST"

    excel_file = request.FILES.get('file')
    project = Project.objects.filter(pk=project_id).first()

    if not excel_file:
        html_message = render_message(request, message='Vui lý nhập file Excel', message_type='red')
        return HttpResponse(html_message)
    if not project:
        html_message = render_message(request, message='Dự án này không tồn tại', message_type='red')
        return HttpResponse(html_message)

    # Read the data from the Excel file then save as job record
    df = pd.read_excel(excel_file, header=1)

    # The table uses verbose names in the excel file, so we need to convert the verbose names to real names
    # Loop through the fields in job
    for field in Job._meta.get_fields():
        if not hasattr(field, 'verbose_name'):
            continue
        if field.verbose_name in df.columns:
            df.rename(columns={field.verbose_name: field.name}, inplace=True)
    # remove duplicate with same name and category
    df = df.drop_duplicates(subset=['name', 'category'], keep='first')
    
    # Before saving any data, we must check if the data of each column is valid
    errors = ''
    jobs = []
    for index, row in df.iterrows():
        job = Job()
        job.project = project
        for field in df.columns:
            value = row[field]
            # if value is NaN
            if pd.isna(value):
                value = ''

            # If field has choice field, we need to convert the string to the correct value
            if field == 'status':
                real_status = ""
                for choice in job.STATUS_CHOICES:
                    if value == choice[1]:
                        real_status = choice[0]
                        break
                if real_status:
                    setattr(job, field, real_status)
                else:
                    setattr(job, field, value) # to raise error
            else:
                setattr(job, field, value) 
        try:
            job.clean()
        except ValidationError as e:
            errors += f'Hàng {str(index + 1)}:\n {e.message}' + '\n'
        jobs.append(job)
        
    if errors:
        html_message = render_message(request, message=errors, message_type='red')
        return HttpResponse(html_message)
    else:
        for job in jobs:
            job.save()
        html_message = render_message(request, message="Cập nhật thành công", ok_button_function='reload')
        return HttpResponse(html_message)


def get_binhanh_service_operation_time(check_date, vehicles):
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
            'IsFuel': True 
        }
        response = call_api(url, payload, auth)
        if response.status_code == 200:
            data = response.json()  
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
            operation_time = {}
            count = 0
            for vehicle in vehicles:
                url = 'https://gps.binhanh.vn/HttpHandlers/RouteHandler.ashx?method=getRouterByCarNumberLite&carNumber={}&fromDate={}%2000:00&toDate={}%2023:59&split=false&isItinerary=false'.format(vehicle, start_date, end_date)
                response = session.get(url, headers=headers)
                data = response.json().get("data")
                count += 1
                # print('Vehicle {}/{}:'.format(count, len(vehicles)), vehicle)

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


    if vehicles == []:
        vehicles = get_vehicle_list()

    # start_date = '01/05/2024' 
    # end_date = '01/05/2024'

    # Get operation time
    operation_time = get_operation_time(vehicles, check_date, check_date)
    return operation_time



def get_vehicle_list_from_binhanh(request):
    def call_api(url, payload, auth):
        response = requests.post(
            url, 
            json=payload, 
            auth=auth
        )
        return response

    # get api type from params
    customer_code = '71735_6'
    api_key = 'Ff$BkG1rAu'
    auth=HTTPBasicAuth(customer_code, api_key)
    url = 'http://api.gps.binhanh.vn/apiwba/gps/tracking'
    payload = {
        'IsFuel': True 
    }
    response = call_api(url, payload, auth)
    if response.status_code == 200:
        data = response.json()  
        message_result = data.get('MessageResult')
        if message_result == 'Success':
            vehicles = data.get('Vehicles', [])
            # Extracting PrivateCode values
            private_codes = [vehicle["PrivateCode"] for vehicle in vehicles ]
            return JsonResponse(private_codes, safe=False)
        else:
            return []
    else:
        return []



def get_trip_data_from_binhanh(request):
    
    def parse_operation_time(vehicle, data):
        if settings.DOMAIN == 'localhost':
            with open('local/log_api.json', 'a') as f:
                f.write("\n\n=========== vehicle: " + vehicle + "===========\n")
                f.write("=========== run time:" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "===========\n")
                json.dump(data, f, indent=4)

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

    def save_operation_record(operation_time):
        # Parse JSON data from the request body
        result = ''
        for vehicle, other_values_list in operation_time.items():
            log_result_data = ''
            for other_values in other_values_list:
                start_time = other_values.get('start_time')
                start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                end_time = other_values.get('end_time')
                end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                duration_seconds = other_values.get('duration_seconds')
                

                # check if the records which has start_time in the check_date
                vehicle_operation_record = VehicleOperationRecord.objects.filter(
                    vehicle=vehicle,
                    start_time=start_time
                ).first()

                # Use this to make sure the vehicle_operation_record is not None
                if not vehicle_operation_record:
                    vehicle_operation_records = VehicleOperationRecord.objects.filter(
                        vehicle=vehicle,
                        start_time__date=start_time.date()
                    )
                    for each_vehicle_operation_record in vehicle_operation_records:
                        if each_vehicle_operation_record.start_time == start_time and each_vehicle_operation_record.vehicle == vehicle:
                            vehicle_operation_record = each_vehicle_operation_record
                    
                if vehicle_operation_record:
                    vehicle_operation_record.end_time = end_time
                    vehicle_operation_record.duration_seconds = duration_seconds
                    vehicle_operation_record.save()
                    log_result_data += f'- Update record with id {vehicle_operation_record.id}: ' + str(vehicle) + ' - ' + str(start_time) + ' - ' + str(end_time) + ' - ' + str(duration_seconds) + '\n'
                else:
                    # Create and save the VehicleOperationRecord instance
                    VehicleOperationRecord.objects.create(
                        vehicle=vehicle,
                        start_time=start_time,
                        end_time=end_time,
                        duration_seconds=duration_seconds
                    )
                    log_result_data += f'- Create record: ' + str(vehicle) + ' - ' + str(start_time) + ' - ' + str(end_time) + ' - ' + str(duration_seconds) + '\n'
            result += vehicle + ' => Success - Details below:\n' + log_result_data + '\n'
        return result

    # get check_date from url
    gps_name = request.GET.get('gps_name')
    check_date = request.GET.get('check_date')
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
            # return JsonResponse(data)
            operation_time = parse_operation_time(gps_name, data)
            # return JsonResponse(operation_time, safe=False)
            result = save_operation_record(operation_time)
            return HttpResponse(result)
        else:
            result = 'Request failed with status code: ' + str(response.status_code)
            result += '\nResponse: ' + str(response.text)
            print(result)
            return  HttpResponse(result)

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        result = 'An error occurred: ' + str(e)
        return HttpResponse(result)

@csrf_exempt
def save_vehicle_operation_record(request):
    # only accept POST request
    if request.method != 'POST':
        return HttpResponse('Method not allowed')
    
    # get check_date from url
    check_date = request.POST.get('check_date')
    vehicles = request.POST.getlist('vehicle')
    check_date = get_valid_date(check_date)
    # convert check_date to datetime date
    check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
    # convert check_date to ddd/mm/yyyy
    check_date = check_date.strftime('%d/%m/%Y')

    data = get_binhanh_service_operation_time(check_date, vehicles)
    # Parse JSON data from the request body
    result = ''
    for vehicle, other_values_list in data.items():
        for other_values in other_values_list:
            start_time = other_values.get('start_time')
            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_time = other_values.get('end_time')
            end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            duration_seconds = other_values.get('duration_seconds')
            
            # check if the records which has start_time in the check_date
            vehicle_operation_record = VehicleOperationRecord.objects.filter(
                vehicle=vehicle,
                start_time=start_time
            ).first()

            if vehicle_operation_record:
                vehicle_operation_record.end_time = end_time
                vehicle_operation_record.duration_seconds = duration_seconds
                vehicle_operation_record.save()
            else:
                # Create and save the VehicleOperationRecord instance
                VehicleOperationRecord.objects.create(
                    vehicle=vehicle,
                    start_time=start_time,
                    end_time=end_time,
                    duration_seconds=duration_seconds
                )
        result += vehicle + '\n'
    return HttpResponse(check_date + ' => done')





# PAGES ==============================================================
@login_required
def page_home(request, sub_page=None):
    user = request.user

    if sub_page == None:
        return redirect('page_home', sub_page='Announcement')

    display_name_dict = {
        'Announcement': 'Thông báo',
        'Task': 'Công việc',
        'User': 'Tài khoản nhân viên',
        'UserPermission': 'Cấp quyền quản lý dữ liệu',
        'ProjectUser': 'Cấp quyền quản lý dự án',
    }

    context = {
        'sub_page': sub_page,
        'model': sub_page,
        'display_name_dict': display_name_dict,
        'current_url': request.path,
    }
    return render(request, 'pages/page_home.html', context)



@login_required
def page_general_data(request, sub_page=None):
    if sub_page == None:
        return redirect('page_general_data', sub_page='VehicleType')

    display_name_dict = {
        'VehicleType': 'DL loại xe',
        'VehicleRevenueInputs': 'DL tính DT theo loại xe',
        'VehicleDetail': 'DL xe chi tiết',
        'StaffData': 'DL nhân viên',
        'DriverSalaryInputs': 'DL mức lương tài xế',
        'DumbTruckPayRate': 'DL tính lương tài xế xe ben',
        'DumbTruckRevenueData': 'DL tính DT xe ben',
        'Location': 'DL địa điểm',
        'NormalWorkingTime': 'Thời gian làm việc',
        'Holiday': 'Ngày lễ',
    }
    context = {
        'sub_page': sub_page,
        'model': sub_page,
        'display_name_dict': display_name_dict,
        'current_url': request.path,
    }
    return render(request, 'pages/page_general_data.html', context)


@login_required
def page_transport_department(request, sub_page=None):
    if sub_page == None:
        return redirect('page_transport_department', sub_page='FuelFillingRecord')

    display_name_dict = {
        'FuelFillingRecord': 'LS đổ nhiên liệu',
        'LubeFillingRecord': 'LS đổ nhớt',
        'RepairPart': 'Danh mục sửa chữa',
        'VehicleMaintenance': 'Phiếu sửa chữa',
        'VehicleDepreciation': 'Khấu hao',
        'VehicleBankInterest': 'Lãi ngân hàng',
        'VehicleOperationRecord': 'DL HĐ xe công trình / ngày',
        'ConstructionDriverSalary': 'Bảng lương',
        'ConstructionReportPL': 'Bảng BC P&L xe cơ giới',
    }

    params = request.GET.copy()
    if 'start_date' not in params:
        start_date = get_valid_date('')
    else:
        start_date = params['start_date']
    if 'end_date' not in params:
        end_date = get_valid_date('')
    else:
        end_date = params['end_date']
    if 'check_month' not in params:
        check_month = get_valid_month('')
    else:
        check_month = params['check_month']

    context = {
        'sub_page': sub_page,
        'model': sub_page,
        'display_name_dict': display_name_dict,
        'current_url': request.path,
        'start_date': start_date, 
        'end_date': end_date, 
        'check_month': check_month}
    return render(request, 'pages/page_transport_department.html', context)


def test(request):
    records = VehicleOperationRecord.objects.all()
    for record in records:
        record.delete()
    return render(request, 'pages/test.html')


@login_required
def page_projects(request):
    return render(request, 'pages/page_projects.html')


@login_required
def page_each_project(request, pk):
    check_date = request.GET.get('check_date')
    project_id = get_valid_id(pk)
    project = get_object_or_404(Project, pk=project_id)
    # Should check if the project is belong to the user
    context = {'project_id': project_id, 'check_date': check_date, 'project':project}
    return render(request, 'pages/page_each_project.html', context)
