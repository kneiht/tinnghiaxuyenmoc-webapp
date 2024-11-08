
import datetime


from datetime import timedelta
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views import View

from .forms import *
from .models import *

from .utils import *


def render_title_bar(request, **kwargs):
    params = kwargs
    page = params.get('page', '')
    model = params.get('model', '')
    project_id = get_valid_id(params.get('project_id', 0))
    project = Project.objects.filter(pk=project_id).first()
    check_date = get_valid_date(params.get('check_date', ''))
        
    context = {
        'page': page,
        'model': model,
        'title': translate('Tiêu đề cho trang: ' + page),
        'create_new_button_name': translate(f'Thêm {model}'),
        'project_id': project_id,
        'check_date': check_date if check_date else datetime.now().date().strftime('%Y-%m-%d')
    }

    if page=='page_each_project': 
        project = Project.objects.filter(pk=project_id).first()
        context['title'] = translate(f'Quản lý dự án: {project.name}')

    # Render
    template = 'components/title_bar.html'
    return render_to_string(template, context, request)





def render_tool_bar(request, **kwargs):
    params = kwargs
    page = params.get('page', '')
    model = params.get('model', '')
    project_id = get_valid_id(params.get('project_id', 0))
    check_date = get_valid_date(params.get('check_date', ''))
    start_date = get_valid_date(params.get('start_date', ''))
    group_by = params.get('group_by', '')
    tab = params.get('tab', '')
    # print(check_date)
    project = Project.objects.filter(pk=project_id).first()
    context = {
        'page': page,
        'model': model,
        'project_id': project_id,
        'check_date': check_date if check_date else datetime.now().date().strftime('%Y-%m-%d'),
        'start_date': start_date,
        'group_by': group_by,
        'tab': tab
    }
    if model not in ['Project', 'Job', 'VehicleOperationRecord']:
        context['create_new_button_name'] = translate(f'Thêm {model}')
    # print(context)
    # Render 
    template = 'components/tool_bar.html'
    return render_to_string(template, context, request)






def render_infor_bar(request, **kwargs):
    params = kwargs
    page = params.get('page', '')
    project_id = get_valid_id(params.get('project_id', 0))
    check_date = get_valid_date(params.get('check_date', ''))
    if page == 'page_each_project':
        project = Project.objects.filter(pk=project_id).first()
        number_of_jobs = project.get_number_of_jobs()
        context = {
            'project': project,
            'check_date': check_date,
            'project_id': project_id,
            'page': page,
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
        return render_to_string(template, context, request)
    else:
        return HttpResponse("")





def render_display_records(request, **kwargs):
    params = kwargs
    model = params.get('model', '')
    update = params.get('update', False)
    project_id = get_valid_id(params.get('project_id', 0))
    check_date = get_valid_date(params.get('check_date', ''))
    start_date = get_valid_date(params.get('start_date', ''))
    group_by = params.get('group_by', '')
    records = params.get('records', None)
    tab = params.get('tab', '')
    # Check the page to render specific content
    model_class = globals()[model]
    project = Project.objects.filter(pk=project_id).first()
    
    if not records:
        if not project_id:
            records = model_class.objects.all()
        else:
            records = model_class.objects.filter(project=project)
        records = filter_records(request, records, model_class)

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

    groups = {}
    if group_by:
        print('group_by:', group_by)
        # get all values of the field
        values = [getattr(record, group_by) for record in records]

        # get unique values
        group_keys = set(values)
        # remove None values
        group_keys = [value for value in group_keys if value != None]
        # order
        try:
            group_keys = sorted(group_keys)
        except Exception as e:
            print(e)
        for group_key in group_keys:
            groups[group_key] = records.filter(**{group_by: group_key})

    # Render 
    template = 'components/display_records.html'
    context = {'model': model, 
               'records': records, 
               'groups': groups,
               'fields': fields, 
               'headers': headers, 
               'update': update, 
               'group_by': group_by,
               'project_id': project_id,
               'project': project,
               'check_date': check_date,
               'tab': tab,
    }
    # print(context)
    return render_to_string(template, context, request)



def render_form(request, **kwargs):
    # Todo: should have list of model that can be accessed
    # Convert model name to model class
    model = kwargs.get('model', '')
    pk = get_valid_id(kwargs.get('pk', 0))
    form = kwargs.get('form', '')
    model_class = globals()[model]
    form_class = globals()[model + 'Form']
    project_id = get_valid_id(kwargs.get('project_id', 0))

    # Set selections
    modal = 'modal_' + model

    # Get the instance if pk is provided, use None otherwise
    record = model_class.objects.filter(pk=pk).first()
    # Get the form
    if not form:
        form = form_class(instance=record) if record else form_class()
        
    context = {
        'submit_button_name': 'Cập nhật' if record else 'Tạo mới',
        'title': translate(f'Cập nhật {model}') if record else translate(f'Tạo {model} mới'),
        'form_url': reverse('handle_form', kwargs={'model': model, 'pk': pk}),
        'model': model,
        'project_id': project_id,
        'modal': modal,
        'form': form,
        'record': record
    }

    template = 'components/modal.html'
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


