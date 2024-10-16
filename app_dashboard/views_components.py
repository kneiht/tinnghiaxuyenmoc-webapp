# security issues
# https://chat.openai.com/share/16295269-0f56-4c6a-8cd7-7ea903fdaf86
# cần check truy cập trang cần đúng school_id and user


import time, datetime, os, json, re

from io import BytesIO
import pandas as pd
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse


from django.contrib.auth.models import User


from .models import Project, ProjectUser, Job, JobProgress, DataVehicle, DataDriver, DataVehicleTypeDetail
from .forms import ProjectForm, JobForm, DataVehicleForm, DataDriverForm, DataVehicleTypeDetailForm

from django.db.models import Q

from .utils import is_admin, is_project_user


# GENERAL PAGES ==============================================================



def render_title_bar(request, title_bar, **kwargs):
    project = kwargs.get('project')
    # Create text dictionary
    if title_bar=='title_bar_page_projects':
        text_dict = {
                'title': 'Trang quản lý các dự án',
                'title_bar': title_bar,
                'create_new_button_name': 'Thêm dự án',
                'create_new_form_url': reverse('load_form') + '?modal=modal_project&pk=0',
            }
    elif title_bar=='title_bar_page_each_project':   
        text_dict = {
            'title': 'Trang quản lý dự án: ' + project.name if project else None,
            'title_bar': title_bar,
            'create_new_button_name': 'Thêm công việc',
            'create_new_form_url':  reverse('load_form') + '?modal=modal_job&pk=0&project_id=' + str(project.pk),
        }
    else:
        return ''
    
    # Render
    template = 'components/title_bar.html'
    context = {'title_bar': title_bar, 'text': text_dict}
    if project:
        context['project'] = project
    return render_to_string(template, context, request)


def render_tool_bar(request, tool_bar, **kwargs):
    project = kwargs.get('project')
    # Create text dictionary
    if tool_bar=='tool_bar_page_projects':
        text_dict = {
            'query_url': reverse('load_content', kwargs={'page': 'page_projects'}),
            'create_new_button_name': 'Thêm dự án',
            'create_new_form_url': reverse('load_form') + '?modal=modal_project&pk=0',
        }
    elif tool_bar=='tool_bar_page_each_project':
        text_dict = {
            'query_url': reverse('load_content', kwargs={'page': 'page_each_project', 'project_id': project.pk}),
            'create_new_button_name': 'Thêm dự án',
            'create_new_form_url': reverse('load_form') + '?modal=modal_job&pk=0&project_id=' + str(project.pk)
        }
    else:
        return ''
    
    # Render 
    template = 'components/tool_bar.html'
    context = {'tool_bar': tool_bar, 'text': text_dict}
    return render_to_string(template, context, request)



def render_record(request, record_type, record, **kwargs):
    if record_type=='record_project':
        model_class = Project
        record.edit_form_url = reverse('load_form') + '?modal=modal_project' + '&pk=' + str(record.pk)
    elif record_type=='record_job':
        model_class = Job
        record.edit_form_url = reverse('load_form') + '?modal=modal_job' + '&pk=' + str(record.pk) + '&project_id=' + str(record.project.pk)
    # Get fields to be displayed by using record meta
    fields = []
    for field in model_class._meta.get_fields():
        if field.name in ['id', 'secondary_id', 'project', 'created_at']:
            continue
        if getattr(field, 'verbose_name', None):
            print(field)
            fields.append(field.name)

    # Render 
    template = 'components/record.html'
    
    context = {'record_type': record_type, 'record': record, 'fields': fields, 'outer_tag': kwargs.get('outer_tag')}
    return render_to_string(template, context, request)




def render_display_records(request, record_type, **kwargs):
    records = kwargs.get('records')
    user = request.user
    if record_type=='record_project':
        model_class = Project
        for record in records:
            record.edit_form_url = reverse('load_form') + '?modal=modal_project' + '&pk=' + str(record.pk)
    elif record_type=='record_job' or 'record_job_insert':
        model_class = Job
        for record in records:
            record.edit_form_url = reverse('load_form') + '?modal=modal_job' + '&pk=' + str(record.pk) + '&project_id=' + str(record.project.pk)
    
    # Get fields to be displayed by using record meta
    fields = []
    headers = []
    for field in model_class._meta.get_fields():
        if field.name in ['id', 'secondary_id', 'project', 'created_at']:
            continue
        if getattr(field, 'verbose_name', None):
            print(field)
            fields.append(field.name)
            headers.append(getattr(field, 'verbose_name'))

    # Render 
    template = 'components/display_records.html'
    context = {'record_type': record_type, 'records': records, 'fields': fields, 'headers': headers}
    return render_to_string(template, context, request)





def render_form(request, pk, modal, **kwargs):
    if modal=='modal_project':
        model_class = Project
        form_class = ProjectForm
    elif modal=='modal_job':
        model_class = Job
        form_class = JobForm
    # Get the instance if pk is provided, use None otherwise
    record = model_class.objects.filter(pk=pk).first()
    text_dict = {
        'modal_project': {
            'submit_button_name': 'Cập nhật' if record else 'Tạo mới',
            'title': 'Cập nhật dự án' if record else 'Tạo dự án mới',
            'form_url': reverse('handle_form') + '?pk=' + str(record.pk if record else 0) + '&model=project'
        },
        'modal_job': {
            'project_id': kwargs.get('project_id'),
            'submit_button_name': 'Cập nhật' if record else 'Tạo mới',
            'title': 'Cập nhật công việc' if record else 'Tạo công việc mới',
            'form_url': reverse('handle_form') + '?pk=' + str(record.pk if record else 0) + '&model=job',
            'project_id': kwargs.get('project_id'),
        },



        'modal_data_vehicle': {
            'submit_button_name': 'Cập nhật' if record else 'Tạo mới',
            'title': 'Cập nhật thông tin xe' if record else 'Thêm xe mới',
            'form_url': reverse('api_data_vehicle_pk', kwargs={'pk': record.pk}) if record else reverse('api_data_vehicles'),
        },
        'modal_data_driver': {
            'submit_button_name': 'Cập nhật' if record else 'Tạo mới',
            'title': 'Cập nhật thông tin tài xế' if record else 'Thêm tài xế mới',
            'form_url': reverse('api_data_driver_pk', kwargs={'pk': record.pk}) if record else reverse('api_data_drivers'),
        },
        'modal_data_vehicle_type_detail': {
            'submit_button_name': 'Cập nhật' if record else 'Tạo mới',
            'title': 'Cập nhật thông tin chi tiết xe' if record else 'Thêm thông tin chi tiết xe mới',
            'form_url': reverse('api_data_vehicle_type_detail_pk', kwargs={'pk': record.pk}) if record else reverse('api_data_vehicle_type_details'),
        },
    }

    # Get the form
    form = form_class(instance=record) if record else form_class()
    template = 'components/modal.html'
    context = {'modal': modal, 'form': form, 'record': record, 'text': text_dict[modal]}
    return render_to_string(template, context, request)


def render_message(request, message):
    context = {'message': message}
    template = 'components/message.html'
    return render_to_string(template, context, request)





