# security issues
# https://chat.openai.com/share/16295269-0f56-4c6a-8cd7-7ea903fdaf86
# cần check truy cập trang cần đúng school_id and user


import time, datetime, os, json, re
from datetime import timedelta
from io import BytesIO
import pandas as pd
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse


from django.contrib.auth.models import User


from .models import *
from .forms import *
from django.db.models import Q

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


    duration = (record.end_date - record.start_date).days + 1
    if duration == 0:
        progress = 1
        percent = 100
    else:
        progress = int((check_date - record.start_date).days) + 1
        percent = int((progress / duration) * 100) if progress<=duration else 100


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
    planned_quantity_to_now_project = 0
    project_quantity = 0
    for job in jobs:
        duration_job = (job.end_date - job.start_date).days + 1
        if duration_job == 0:
            continue
        days_to_now_job = (check_date - job.start_date).days + 1
        planned_quantity_to_now_job = int((days_to_now_job / duration_job) * job.quantity)
        if planned_quantity_to_now_job >= job.quantity:
            planned_quantity_to_now_job = job.quantity
        planned_quantity_to_now_project += planned_quantity_to_now_job
        project_quantity += job.quantity
    
    if project_quantity == 0:
        return None
    percent = int((planned_quantity_to_now_project / project_quantity) * 100)


    res = {
        'planned_quantity_to_now_project': planned_quantity_to_now_project,
        'quantity': project_quantity,
        'percent': percent
    }
    return res









def render_infor_bar(request, page, project_id):
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
        }

    # Render
    template = 'components/infor_bar.html'
    context = {'page': page, 'text': text_dict}
    return render_to_string(template, context, request)





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
    print('>>>>', headers)


    if model_class == Job:
        for record in records:
            record.progress_by_time = progress_by_time(record, check_date=check_date)
            record.progress_by_quantity = progress_by_quantity(record, check_date=check_date)

    elif model_class == Project:
        for record in records:
            record.progress_by_time = progress_by_time(record)
            record.progress_by_quantity = progress_by_quantity(record)
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
    
    # Add all params from the request to text dict
    for key, value in request.GET.items():
        text_dict[key] = value

    # Get the form
    if not form:
        form = form_class(instance=record) if record else form_class()
    template = 'components/modal.html'
    context = {'modal': modal, 'form': form, 'record': record, 'text': text_dict}
    return render_to_string(template, context, request)


def render_message(request, message, message_type='green'):
    context = {'message': message, 'message_type': message_type}
    template = 'components/message.html'
    return render_to_string(template, context, request)




def render_weekplan_table(request, project_id, check_date=None):
    project = Project.objects.filter(pk=project_id).first()

    try:
        check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
    except:
        check_date = timezone.now().date()

    print('>>>>>>>>>>>>>> check_date', check_date, type(check_date))
    # Get monday and sunday dates of the week that contains check_date
    monday = check_date - timedelta(days=check_date.weekday())
    sunday = check_date + timedelta(days=6 - check_date.weekday())
    last_sunday = sunday - timedelta(days=7)
    week = f'{monday.strftime("%d-%m-%Y")} đến {sunday.strftime("%d-%m-%Y")}'
    jobplans_in_week = JobPlan.objects.filter(start_date__gte=monday, end_date__lte=sunday, job__project=project)
    job_date_reports = JobDateReport.objects.filter(date=check_date, job__project=project)


    print('>>>>>>> job_date_reports', job_date_reports)

    jobs = Job.objects.filter(project=project)

    for job in jobs:
        job.progress_left_by_quantity_upto_lastweek = job.quantity - progress_by_quantity(job, check_date=last_sunday)['total_quantity_reported']
        
        # Get jobplan in week
        jobplan_in_week = jobplans_in_week.filter(job=job).first()
        
        if jobplan_in_week:
            job.plan_note = jobplan_in_week.note
            job.plan_quantity = jobplan_in_week.plan_quantity
        else:
            job.plan_quantity = ""
            job.plan_note = ""

    for jobplan in jobplans_in_week:
        # Get date report
        job_date_report = job_date_reports.filter(job=jobplan.job, date=check_date).first()
        if job_date_report:
            jobplan.date_quantity = job_date_report.quantity
            jobplan.date_note = job_date_report.note
        else:
            jobplan.date_quantity = ""
            jobplan.date_note = ""


    for jobplan_in_week in jobplans_in_week:
        jobplan_in_week.progress_by_time = progress_by_time(jobplan_in_week, check_date=check_date)
        jobplan_in_week.progress_by_quantity = progress_by_quantity(jobplan_in_week, check_date=check_date)
        

    print('>>>>>>>>>>>>>> jobplans_in_week', jobplans_in_week)


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