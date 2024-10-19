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
    }
    return text





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
        'create_new_button_name': f'Thêm {model}',
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
        'create_new_button_name': f'Thêm {model}',
        'create_new_form_url': reverse('load_form', kwargs={'model': model, 'pk': 0}) + param_string,
        'project_id': project_id if project_id else '',
    }

    # Render 
    template = 'components/tool_bar.html'
    context = {'page': page, 'text': text_dict}
    return render_to_string(template, context, request)




def render_display_records(request, model_class, records, update=None):
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


    # Render 
    template = 'components/display_records.html'
    context = {'model': model, 'records': records, 'fields': fields, 'headers': headers, 'update': update}
    return render_to_string(template, context, request)



def render_form(request, model, pk=0):
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
    form = form_class(instance=record) if record else form_class()
    template = 'components/modal.html'
    context = {'modal': modal, 'form': form, 'record': record, 'text': text_dict}
    return render_to_string(template, context, request)


def render_message(request, message):
    context = {'message': message}
    template = 'components/message.html'
    return render_to_string(template, context, request)




def render_weekplan_table(request, project_id, check_date=None):
    project = Project.objects.filter(pk=project_id).first()

    try:
        check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
        print('>>>>', check_date)
        print('>>>>', type(check_date))
    except:
        check_date = timezone.now().date()
        print('>>>>', check_date)
        print('>>>>', type(check_date))

    
    # Get monday and sunday dates of the week that contains check_date
    monday = check_date - timedelta(days=check_date.weekday())
    sunday = check_date + timedelta(days=6 - check_date.weekday())
    week = f'{monday.strftime("%d-%m-%Y")} đến {sunday.strftime("%d-%m-%Y")}'
    jobplans_in_week = JobPlan.objects.filter(start_date__gte=monday, end_date__lte=sunday, job__project=project)
    job_date_reports = JobDateReport.objects.filter(date__gte=check_date)
    jobs = Job.objects.filter(project=project)

    for job in jobs:
        # Get jobplan in week
        jobplan_in_week = jobplans_in_week.filter(job=job).first()
        
        if jobplan_in_week:
            job.plane_note = jobplan_in_week.note
            job.plan_quantity = jobplan_in_week.plan_quantity
        else:
            job.plan_quantity = ""
            job.plane_note = ""

        # Get date report
        job_date_report = job_date_reports.filter(job=job, date=check_date).first()
        if job_date_report:
            job.date_quantity = job_date_report.quantity
            job.date_note = job_date_report.note
        else:
            job.date_quantity = ""
            job.date_note = ""


    template = 'components/weekplan_table.html'
    context = {'jobplans_in_week': jobplans_in_week, 
               'job_date_reports': job_date_reports,
               'jobs':jobs,
               'week': week,
               'monday': monday.strftime('%Y-%m-%d'), 
               'sunday': sunday.strftime('%Y-%m-%d'), 
               'check_date': check_date.strftime('%Y-%m-%d'),
               'check_date_format': check_date.strftime('%d-%m-%Y'),
               'project_id': project_id}

    return render_to_string(template, context, request)