# security issues
# https://chat.openai.com/share/16295269-0f56-4c6a-8cd7-7ea903fdaf86
# cần check truy cập trang cần đúng school_id and user


import time, datetime, os, json, re

from io import BytesIO
import pandas as pd
from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

from django.views import View
from .html_render import html_render

from .models import Project, ProjectUser, Job, JobProgress, DataVehicle, DataDriver, DataVehicleTypeDetail
from .forms import ProjectForm, JobForm, DataVehicleForm, DataDriverForm, DataVehicleTypeDetailForm

from django.db.models import Q, Count, Sum  # 'Sum' is imported here


from .utils import is_admin, is_project_user
from .views_components import (
    render_form, render_title_bar, 
    render_tool_bar,
    render_display_records,
    render_message,
    render_record
)


def filter_records(request, records, model_class):
    # Get all query parameters except 'sort' as they are assumed to be field filters
    query_params = {k: v for k, v in request.GET.lists() if k != 'sort'}
    # Determine the fields to be used as filter options based on the selected page
    if model_class == Project:
        fields = ['all', 'name', 'description']
    elif model_class == Job:
        fields = ['all', 'name', 'status', 'category', 'unit', 'quantity', 'description']
    else:
        fields = ['all']

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
def handle_form(request):
    # check if not Post => return 404
    if request.method != 'POST':
        return HttpResponseForbidden()

    # get params
    pk = request.GET.get('pk')
    model = request.GET.get('model')

    # Set selections
    if model == 'project':
        form_class = ProjectForm
        model_class = Project
        record_type = 'record_project'
        modal = 'modal_project'
    else:
        form_class = JobForm
        model_class = Job
        record_type = 'record_job'
        modal = 'modal_job'

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
        if pk == '0' or pk == '' or pk==0:
            html_record = render_record(request, record_type=record_type, record=record, outer_tag=True)
        else:
            html_record = render_record(request, record_type=record_type, record=record, outer_tag=True)
        
        print(html_record)
        return HttpResponse(html_message + html_record)
    else:
        print(form.errors)
        html_modal = render_form(request, pk, modal=modal)
        return  HttpResponse(html_modal)





@login_required
def load_content(request, page, project_id=None):
    print(page)
    if page is None:
        return HttpResponseForbidden()
    # Check if there is project id i the params, if yes => get the project
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
    
    # render general content
    html_load_content = '<div id="load-content" class"hidden"></div>'
    html_title_bar = render_title_bar(request, title_bar='title_bar_' + page, project=project if project_id else None)
    html_tool_bar = render_tool_bar(request, tool_bar='tool_bar_' + page, project=project if project_id else None)
    # Check the page to render specific content
    if page=='page_projects': 
        records = Project.objects.all()
        records = filter_records(request, records, Project)
        html_display_records = render_display_records(request, record_type='record_project', records=records)
        
    elif page=='page_each_project':
        records = Job.objects.filter(project=project)
        print(records)
        records = filter_records(request, records, Job)
        print(records)
        html_display_records = render_display_records(request, record_type='record_job', records=records)
    return HttpResponse(html_load_content + html_title_bar + html_tool_bar + html_display_records)


@login_required
def load_form(request):
    pk = request.GET.get('pk')
    modal = request.GET.get('modal')
    project_id = request.GET.get('project_id')
    html_modal = render_form(request, pk, modal=modal, project_id=project_id)
    return HttpResponse(html_modal)





# GENERAL PAGES ==============================================================
@login_required
def page_projects(request):
    user = request.user
    return render(request, 'pages/page_projects.html')



@login_required
def page_each_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Should check if the project is belong to the user
    context = {'project': project}
    return render(request, 'pages/page_each_project.html', context)

@login_required
def page_manage_data(request):
    data_vehicles = DataVehicle.objects.all()
    data_drivers = DataDriver.objects.all()
    data_vehicle_type_details = DataVehicleTypeDetail.objects.all()
    context = {'title': "Quản lý dữ liệu",
               'title_bar': 'title_bar_data',
               'create_new_button_name': 'Thêm xe',
               'create_new_form_url': reverse('api_data_vehicles') + '?get=form',
               'tool_bar': 'tool_bar_vehicle',
               'data_vehicles': data_vehicles,
               'data_drivers': data_drivers,
               'data_vehicle_type_details': data_vehicle_type_details} 
    return render(request, 'pages/page_manage_data.html', context)


@login_required
def update_project_progress(request, pk):
    project = Project.objects.filter(pk=pk).first()
    project.save()
    return JsonResponse({'success': True})


@login_required
def download_project(request, pk):
    project = Project.objects.filter(pk=pk).first()
    jobs = Job.objects.filter(project_id=pk)
    table_names = ['job']
    def fetch_table_data(table_name):
        if table_name == 'job':
            data = jobs.values(
                'id', 'name', 'category', 'unit', 'quantity', 'description', 'start_date', 'end_date', 'created_at'
            )
            df = pd.DataFrame(data)
            return df


    # Create a Pandas Excel writer using XlsxWriter as the engine
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Loop through tables and write each to a separate sheet
        for table_name in table_names:
            data = fetch_table_data(table_name)
            # Shorten the table name for the Excel sheet
            shortened_table_name = table_name.replace('', '')
            data.to_excel(writer, sheet_name=shortened_table_name, index=False)


    # Get the Excel file
    excel_data = output.getvalue()

    # Return the Excel file as an HTTP response
    response = HttpResponse(
        excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    # name the db based on time
    filename = f"Project_download_{datetime.datetime.now().strftime('%Y_%m_%d')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response



@login_required
def upload_project(request, pk):
    if request.method == 'GET':
        return "API này không dùng GET"

    if request.method == 'POST':
        excel_file = request.FILES.get('file')
        table = 'job'
        project = Project.objects.filter(pk=pk).first()
        if excel_file and excel_file.name.endswith('.xlsx'):
            df = pd.read_excel(excel_file, sheet_name=table)
            for index, row in df.iterrows():
                job = Job(
                    project=project,
                    name=row['name'],
                    category=row['category'],
                    unit=row['unit'],
                    quantity=row['quantity'],
                    description=row['description'],
                    start_date=row['start_date'],
                    end_date=row['end_date'],
                )
                job.save()

            html_message = html_render('message', request, message='Tải dữ liệu lên thành công')
            return redirect('project', pk=project.pk)







