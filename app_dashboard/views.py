# security issues
# https://chat.openai.com/share/16295269-0f56-4c6a-8cd7-7ea903fdaf86
# cần check truy cập trang cần đúng school_id and user

from core import settings
import pandas as pd

import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from .forms import *
from .models import *

from .renders import *
from .utils import *



# HANDLE FORMS ===============================================================
def handle_form(request, model, pk=0):
    # Todo: should have list of model that can be accessed
    # Convert model name to model class
    model_class = globals()[model]
    form_class = globals()[model + 'Form']

    # Set selections
    record_type = 'record_' + model
    modal = 'modal_' + model

    # check if not Post => return 404
    if request.method != 'POST':
        return HttpResponseForbidden()

    # Get form
    instance = model_class.objects.filter(pk=pk).first()
    form = form_class(request.POST, request.FILES, instance=instance)

    if form.is_valid():
        instance_form = form.save(commit=False)
        if instance is None:  # This is a new form
            # Handle the case of the project is created and need to be assigned to a user
            # instance_form.user = request.user
            pass
        instance_form.save()
        # Save the many to many field, if any
        # form.save_m2m()
        record = instance_form
        record.style = 'just-updated'
        html_message = render_message(request, message='Cập nhật thành công')
        html_record = render_display_records(request, model_class, [record], update='True')
        
        return HttpResponse(html_message + html_record)
    else:
        html_modal = render_form(request, model, pk, form)
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
def load_element(request, element):
    # Get page
    page = request.GET.get('page')
    # Get project_id
    project_id = request.GET.get('project_id')
    # Get check_date
    check_date = request.GET.get('check_date')
    # Render
    if element == 'infor_bar':
        html_infor_bar = render_infor_bar(request, page, project_id=project_id, check_date=check_date)
        return HttpResponse(html_infor_bar)
    else:
        return HttpResponse("")


@login_required
def load_form(request, model, pk=0):
    html_modal = render_form(request, model, pk)
    return HttpResponse(html_modal)


@login_required
def load_content(request, page, model, project_id=None):
    check_date = request.GET.get('check_date')
    if page is None:
        return HttpResponseForbidden()
    # Check if there is project id i the params, if yes => get the project
    if project_id:
        project = Project.objects.filter(pk=project_id).first()
    
    # render general content
    html_load_content = '<div id="load-content" class"hidden"></div>'
    html_title_bar = render_title_bar(request, page, model=model, project_id=project_id, check_date=check_date)
    html_tool_bar = render_tool_bar(request, page, model=model, project_id=project_id, check_date=check_date)
    
    if page == 'page_each_project':
        html_infor_bar = render_infor_bar(request, page, project_id=project_id, check_date=check_date)
    else:
        html_infor_bar = ''

    # Check the page to render specific content
    model_class = globals()[model]
    if not project_id:
        records = model_class.objects.all()
    else:
        records = model_class.objects.filter(project=project)
    records = filter_records(request, records, model_class)

    html_display_records = render_display_records(request, model_class, records, update=False, check_date=check_date)
    return HttpResponse(html_load_content + html_title_bar + html_tool_bar + html_infor_bar + html_display_records)





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
    # print(form)
    try:
        start_date = form.get('start_date')
        end_date = form.get('end_date')
        check_date = form.get('check_date')
        project_id = form.get('project_id')

        # get all jobs of the project
        jobs = Job.objects.filter(project_id=project_id)
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
                jobplan.save()
                continue
            else:
                JobPlan(
                    job=job,
                    start_date=start_date,
                    end_date=end_date,
                    plan_quantity=quantity,
                    note=note
                ).save()
        html_weekplan_table = render_weekplan_table(request, project_id, check_date=check_date)
        html_infor_bar = render_infor_bar(request, 'page_each_project', project_id=project_id, check_date=check_date)
        html_message = render_message(request, message='Cập nhật thông tin thành công.\n\nĐã chuyển đến bộ phận phê duyệt kế hoạch')
        return HttpResponse(html_message + html_weekplan_table + html_infor_bar)

    except Exception as e:
        # raise e
        html = render_message(request, message='Có lỗi: ' + str(e))
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
        # print('>>>>>>>>>>>>>>> checkdate and project:', check_date, project_id)
        # get all jobs of the project
        jobs = Job.objects.filter(project_id=project_id)
                    
        for job in jobs:
            jobplan_in_week = JobPlan.objects.filter(start_date__gte=monday, end_date__lte=sunday, job=job).first()
            if not jobplan_in_week:
                html = render_message(request, message='Không cập nhật được báo cáo ngày.\n\nVui lòng chờ báo cáo tuần được phê duyệt trước.', message_type='red')
                return HttpResponse(html)
            
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
            # print('>>>>>>>>>>>>>>> total_amount_reported:', total_quantity_reported, 'total_quantity_left:', total_quantity_left)
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
        html_infor_bar = render_infor_bar(request, 'page_each_project', project_id=project_id, check_date=check_date)
        return HttpResponse(html_message + html_weekplan_table + html_infor_bar) 
    
    except Exception as e:
        # raise e
        html = render_message(request, message='Có lỗi: ' + str(e), message_type='red')
        return HttpResponse(html)
        

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def save_vehicle_operation_record(request):
    if request.method != 'POST':
        return HttpResponseForbidden()

    try:
        # Parse JSON data from the request body
        data = json.loads(request.body)
        print(data)
        for vehicle, other_values_list in data.items():
            for other_values in other_values_list:
                start_time = other_values.get('start_time')
                end_time = other_values.get('end_time')
                duration_seconds = other_values.get('duration_seconds')
                
                # get the date of the start_time
                check_date = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').date()
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
        # Process the data (for example, print it or save it to the database)
        # Here, we will just return it in the response for demonstration
        return JsonResponse({
            'status': 'success',
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)



def handle_vehicle_operation_form(request):
    if request.method != 'POST':
        return HttpResponseForbidden()
    
    try:
        form = request.POST
        print(form)
        # Get list of ids
        ids = form.getlist('id')
        for id in ids:
            print('>>>> id:', id)
            driver_id = form.get(f'driver_{id}', None)
            if driver_id is None: 
                continue
            else:
                # check if driver is not a int string
                try:
                    driver_id = int(driver_id)
                    driver = DataDriver.objects.filter(pk=driver_id).first()
                except:
                    driver = None
            
            record = VehicleOperationRecord.objects.get(pk=id)
            record.driver = driver
            if record.source == 'manual':
                try:
                    duration_time_str = form.get(f'duration_time_{id}', None)
                    hours, minutes, seconds = map(int, duration_time_str.split(":"))
                    total_seconds = hours * 3600 + minutes * 60 + seconds
                    duration_seconds = total_seconds
                    duration_type = form.get(f'duration_type_{id}', None)
                    if duration_type == 'minus':
                        record.duration_type = 'minus'
                    else:
                        record.duration_type = 'plus'
                    record.duration_seconds = duration_seconds
                    
                except:
                    pass
            record.save()
        
        # Add new records
        new_vehicles = form.getlist('vehicle_new')
        new_start_times = form.getlist('start_time_new')
        new_end_times = form.getlist('start_time_new')
        new_duration_seconds = form.getlist('duration_time_new')
        new_driver_ids = form.getlist('driver_new')
        new_duration_types = form.getlist('duration_type_new')
        for i in range(0, len(new_vehicles)): # start from 1 because the first one is a template
            try:
                duration_time_str = new_duration_seconds[i]
                hours, minutes, seconds = map(int, duration_time_str.split(":"))
                total_seconds = hours * 3600 + minutes * 60 + seconds
                duration_seconds = total_seconds
                if duration_seconds == 0:
                    continue
            except:
                continue
            
        
            vehicle = new_vehicles[i]
            driver_id = new_driver_ids[i]

            if driver_id is None: 
                continue
            else:
                # check if driver is not a int string
                try:
                    driver_id = int(driver_id)
                    driver = DataDriver.objects.filter(pk=driver_id).first()
                except:
                    driver = None
            
            start_time = new_start_times[i]
            # convert start time to datetime object
            start_time = datetime.strptime(start_time, '%d/%m/%Y')
            end_time = start_time

            duration_type = new_duration_types[i]
            if duration_type == 'minus':
                record.duration_type = 'minus'
            else:
                record.duration_type = 'plus'

            new_record = VehicleOperationRecord.objects.create(
                vehicle=vehicle,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration_seconds,
                source='manual',
                duration_type=duration_type,
                driver=driver
            )
            ids.append(new_record.id)

        # Get records by ids
        records = VehicleOperationRecord.objects.filter(pk__in=ids)
        html_display = render_display_records(request, VehicleOperationRecord, records)
        html_message = render_message(request, message='Cập nhật thành công', message_type='green')
        html = html_message + html_display
        return HttpResponse(html)
    except Exception as e:
        raise e
        html = render_message(request, message='Có lỗi: ' + str(e), message_type='red') 
        return HttpResponse(html)






# GENERAL PAGES ==============================================================
@login_required
def page_home(request):
    user = request.user
    jobplans = JobPlan.objects.filter(status='wait_for_approval')
    # get dictionary of projects, start_date and end_date of the jobplans
    approval_tasks = []
    for jobplan in jobplans:
        approval_tasks.append({
            'project': jobplan.job.project,
            'start_date': jobplan.start_date,
            'end_date': jobplan.end_date
        })

    context = {'approval_tasks': approval_tasks}
    return render(request, 'pages/page_home.html', context)



@login_required
def page_projects(request):
    user = request.user
    return render(request, 'pages/page_projects.html')

@login_required
def page_each_project(request, pk):
    check_date = request.GET.get('check_date')
    project = get_object_or_404(Project, pk=pk)
    # Should check if the project is belong to the user
    context = {'project': project, 'check_date': check_date}
    return render(request, 'pages/page_each_project.html', context)


@login_required
def page_manage_data(request):
    return render(request, 'pages/page_manage_data.html')


@login_required
def page_transport_department(request):
    return render(request, 'pages/page_transport_department.html')


def test(request):
    return render(request, 'pages/test.html')















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

