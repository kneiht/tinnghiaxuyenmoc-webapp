# security issues
# https://chat.openai.com/share/16295269-0f56-4c6a-8cd7-7ea903fdaf86
# cần check truy cập trang cần đúng school_id and user

from core import settings
import datetime
import json
import os
import re
import time
from io import BytesIO
import pandas as pd


from datetime import timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q, Count, Sum
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views import View

from .forms import *
from .html_render import html_render
from .models import *
from .utils import is_admin, is_project_user




# GENERAL PAGES ==============================================================

def translate(text):
    translated_text = {
        'title_bar_page_projects': 'Trang quản lý các dự án',
        'Tiêu đề cho trang: page_projects': 'Trang quản lý các dự án',
        'Thêm Project': 'Thêm dự án',
        'Thêm Job': 'Thêm công việc',
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
            'status': 'not_started',
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
        project_amount += job.total_amount
    
    if project_amount == 0:
        return None
    percent = int((planned_amount_to_now_project / project_amount) * 100)


    res = {
        'planned_amount_to_now_project': int(planned_amount_to_now_project),
        'total_amount': int(project_amount),
        'percent': percent
    }
    return res








def render_infor_bar(request, page, project_id, check_date=None):
    text_dict = {}
    if page == 'page_each_project':
        project = Project.objects.filter(pk=project_id).first()
        number_of_jobs = project.get_number_of_jobs()
        text_dict = {
            'total_jobs': number_of_jobs['all'],
            'total_jobs_in_progress': number_of_jobs['in_progress'],
            'total_jobs_not_started': number_of_jobs['not_started'],
            'total_jobs_done': number_of_jobs['done'],
            'total_jobs_pending': number_of_jobs['pending'],
            'progress_by_time': progress_by_time(project, check_date=check_date),
            'progress_by_amount': progress_by_amount(project, check_date=check_date),
            'progress_by_plan': progress_by_plan(project, check_date=check_date),
        }

        # Render
        template = 'components/infor_bar.html'
        context = {'page': page, 'text': text_dict, 'project': project}
        # print(context)
        return render_to_string(template, context, request)
    else:
        return HttpResponse("")



def render_title_bar(request, page, model, project_id=None, check_date=None):
    project = Project.objects.filter(pk=project_id).first()
    param_string = f'?project_id={project_id}' if project_id else ''
    text_dict = {
        'title': translate('Tiêu đề cho trang: ' + page),
        'create_new_button_name': translate(f'Thêm {model}'),
        'create_new_form_url': reverse('load_form', kwargs={'model': model, 'pk': 0}) + param_string,
        'project_id': project_id if project_id else '',
        'check_date': check_date if check_date else datetime.now().date().strftime('%Y-%m-%d')
    }
    if page=='page_each_project': text_dict['title'] = translate(f'Quản lý dự án: {project.name}')

    # Render
    template = 'components/title_bar.html'
    context = {'page': page, 'text': text_dict}
    return render_to_string(template, context, request)


def render_tool_bar(request, page, model, project_id=None):
    project = Project.objects.filter(pk=project_id).first()
    # Create text dictionary
    param_string = f'?project_id=project_id' if project_id else ''
    if project_id:
        query_url = reverse('load_content_with_project', kwargs={'page': page, 'model': model, 'project_id': project_id})
    else:
        query_url = reverse('load_content', kwargs={'page': page, 'model': model})
    

    
    text_dict = {
        'query_url': query_url,
        'project_id': project_id if project_id else '',
    }

    if model not in ['Project', 'Job']:
        text_dict['create_new_button_name'] = translate(f'Thêm {model}')
        url = reverse('load_form', kwargs={'model': model, 'pk': 0}) + param_string
        text_dict['create_new_form_url'] = url
        

    # Render 
    template = 'components/tool_bar.html'
    context = {'page': page, 'text': text_dict}
    return render_to_string(template, context, request)




def render_display_records(request, model_class, records, update=None, check_date=None):
    user = request.user
    model = model_class.__name__
    for record in records:
        param_string = f'?project_id={record.project.pk}' if hasattr(record, 'project') else ''
        record.edit_form_url = reverse('load_form', kwargs={'model': model, 'pk': record.pk}) + param_string


    # Get fields to be displayed by using record meta
    # If there is get_display_fields method, use that method
    fields = []
    headers = []
    if hasattr(model_class, 'get_display_fields'):
        for field in model_class.get_display_fields():
            fields.append(field)
            headers.append(model_class._meta.get_field(field).verbose_name)

    if model_class == Job:
        for record in records:
            record.progress_by_time = progress_by_time(record, check_date=check_date)
            record.progress_by_amount = progress_by_amount(record, check_date=check_date)

    elif model_class == Project:
        for record in records:
            record.progress_by_time = progress_by_time(record)
            record.progress_by_amount = progress_by_amount(record)
            record.progress_by_plan = progress_by_plan(record)


    # Render 
    template = 'components/display_records.html'
    context = {'model': model, 'records': records, 'fields': fields, 'headers': headers, 'update': update}
    return render_to_string(template, context, request)



def render_form(request, model, pk=0, form=None):
    # Todo: should have list of model that can be accessed
    # Convert model name to model class
    model_class = globals()[model]
    form_class = globals()[model + 'Form']

    # Set selections
    modal = 'modal_' + model

    # Get the instance if pk is provided, use None otherwise
    record = model_class.objects.filter(pk=pk).first()
    text_dict = {
        'submit_button_name': 'Cập nhật' if record else 'Tạo mới',
        'title': translate(f'Cập nhật {model}') if record else f'Tạo {model} mới',
        'form_url': reverse('handle_form', kwargs={'model': model, 'pk': pk if record else 0}),
    }
    
    # Add all params from the request to text dict, include projet id
    for key, value in request.GET.items():
        text_dict[key] = value  

    # Get the form
    if not form:
        form = form_class(instance=record) if record else form_class()
    else:
        # Get project id from the form
        project_id = request.POST.get('project')
        text_dict['project_id'] = project_id


    template = 'components/modal.html'
    context = {'modal': modal, 'form': form, 'record': record, 'text': text_dict}
    return render_to_string(template, context, request)


def render_message(request, message, **kwargs):
    message_type = kwargs.get('message_type', 'green')
    ok_button_function = kwargs.get('ok_button_function', 'remove_modal')
    context = {'message': message, 'message_type': message_type, 'ok_button_function': ok_button_function}
    template = 'components/message.html'
    return render_to_string(template, context, request)




def render_weekplan_table(request, project_id, check_date=None):
    project = Project.objects.filter(pk=project_id).first()

    try:
        check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
    except:
        check_date = timezone.now().date()

    # print('>>>>>>>>>>>>>> check_date', check_date, type(check_date))
    # Get monday and sunday dates of the week that contains check_date
    monday = check_date - timedelta(days=check_date.weekday())
    sunday = check_date + timedelta(days=6 - check_date.weekday())
    last_sunday = sunday - timedelta(days=7)
    week = f'{monday.strftime("%d-%m-%Y")} đến {sunday.strftime("%d-%m-%Y")}'
    jobplans_in_week = JobPlan.objects.filter(start_date__gte=monday, end_date__lte=sunday, job__project=project)
    job_date_reports = JobDateReport.objects.filter(date=check_date, job__project=project)


    # print('>>>>>>> job_date_reports', job_date_reports)

    jobs = Job.objects.filter(project=project)

    for job in jobs:
        job.progress_left_by_quantity_upto_lastweek = job.quantity - progress_by_amount(job, check_date=last_sunday)['total_amount_reported']
        
        # Get jobplan in week
        jobplan_in_week = jobplans_in_week.filter(job=job).first()
        print('>>>>>>>>>>>>>> jobplan_in_week', jobplan_in_week)
        if jobplan_in_week:
            job.plan_note = jobplan_in_week.note
            job.plan_quantity = jobplan_in_week.plan_quantity
        else:
            job.plan_quantity = ""
            job.plan_note = ""

        print('>>>>>>>>>>>>>> job', job.plan_quantity, job.plan_note)

    for jobplan in jobplans_in_week:
        # Get date report
        job_date_report = job_date_reports.filter(job=jobplan.job, date=check_date).first()
        if job_date_report:
            jobplan.date_quantity = job_date_report.quantity
            jobplan.date_note = job_date_report.note
            jobplan.date_material = job_date_report.material
            jobplan.date_labor = job_date_report.labor
        else:
            jobplan.date_quantity = ""
            jobplan.date_note = ""
            jobplan.date_material = ""
            jobplan.date_labor = ""


    for jobplan_in_week in jobplans_in_week:
        jobplan_in_week.progress_by_time = progress_by_time(jobplan_in_week, check_date=check_date)
        jobplan_in_week.progress_by_amount = progress_by_amount(jobplan_in_week, check_date=check_date)
        

    # print('>>>>>>>>>>>>>> jobplans_in_week', jobplans_in_week)


    template = 'components/weekplan_table.html'
    context = {'jobplans_in_week': jobplans_in_week, 
               'job_date_reports': job_date_reports,
               'jobs':jobs,
               'week': week,
               'monday': monday.strftime('%Y-%m-%d'),
               'tuesday': (monday + timedelta(days=1)).strftime('%Y-%m-%d'),
               'wednesday': (monday + timedelta(days=2)).strftime('%Y-%m-%d'),
               'thursday': (monday + timedelta(days=3)).strftime('%Y-%m-%d'),
               'friday': (monday + timedelta(days=4)).strftime('%Y-%m-%d'),
               'saturday': (monday + timedelta(days=5)).strftime('%Y-%m-%d'),
               'sunday': sunday.strftime('%Y-%m-%d'), 
               'check_date': check_date.strftime('%Y-%m-%d'),
               'check_date_format': check_date.strftime('%d-%m-%Y'),
               'project_id': project_id,}

    return render_to_string(template, context, request)




def filter_records(request, records, model_class):
    # Get all query parameters except 'sort' as they are assumed to be field filters
    query_params = {k: v for k, v in request.GET.lists() if k != 'sort'}
    # Determine the fields to be used as filter options based on the selected page
    if model_class == Project:
        fields = ['all', 'name', 'description']
    elif model_class == Job:
        fields = ['all', 'name', 'status', 'category', 'unit', 'quantity', 'description']
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
    return records



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
            'progress': progress_by_amount(job, check_date=check_date)['percent'],
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
    html_tool_bar = render_tool_bar(request, page, model=model, project_id=project_id)
    
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






def load_weekplan_table(request, project_id):
    check_date = request.GET.get('check_date')
    html_weekplan_table = render_weekplan_table(request, project_id, check_date)
    html_tool_bar = '<div id="tool-bar" class="hidden"></div>'
    return HttpResponse(html_weekplan_table + html_tool_bar)


def handle_weekplan_form(request):
    if request.method != 'POST':
        return HttpResponseForbidden()
    form = request.POST
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
                quantity = int(quantity)
            except:
                quantity = 0

            if type(note) != str: note = ''


            if quantity > job.quantity:
                message = f'Lỗi khi nhập khối lượng kế hoạch cho công việc "{job.name}". Khối lượng kế hoạch phải nhỏ hơn khối lượng công việc ({str(job.quantity)}).'
                html_message = render_message(request, message=message, message_type='red')
                return HttpResponse(html_message)
            


            jobplan = JobPlan.objects.filter(job=job, start_date=start_date, end_date=end_date).first()
            if quantity == 0 and note.strip() == '':
                if jobplan:
                    print('jobplan: ', jobplan)
                    jobplan.delete()
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
        html_message = render_message(request, message='Cập nhật thông tin thành công')
        return HttpResponse(html_message + html_weekplan_table + html_infor_bar)

    except Exception as e:
        # raise e
        html = render_message(request, message='Có lỗi: ' + str(e))
        return HttpResponse(html)
        


def handle_date_report_form(request):
    if request.method != 'POST':
        return HttpResponseForbidden()
    form = request.POST
    try:
        check_date = form.get('check_date')
        project_id = form.get('project_id')
        # print('>>>>>>>>>>>>>>> checkdate and project:', check_date, project_id)
        # get all jobs of the project
        jobs = Job.objects.filter(project_id=project_id)
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
        html = render_message(request, message='Có lỗi: ' + str(e))
        return HttpResponse(html)
        




# GENERAL PAGES ==============================================================
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
        print(">>>>> row:", index)
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

