
import datetime


from datetime import timedelta
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views import View

from django.contrib.auth.models import User
from .forms import *
from .models.models import *
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
        'project_id': project_id,
        'check_date': check_date if check_date else datetime.now().date().strftime('%Y-%m-%d')
    }

    if page=='page_each_project': 
        project = Project.objects.filter(pk=project_id).first()
        context['title'] = translate(f'{project.name}')

    if model != 'Job':
        context['create_new_button_name'] = translate(f'Thêm {model}')

    # Render
    template = 'components/title_bar.html'
    return render_to_string(template, context, request)



def render_tool_bar(request, **kwargs):
    params = kwargs
    page = params.get('page', '')
    sub_page = params.get('sub_page', '')
    model = params.get('model', '')
    project_id = get_valid_id(params.get('project_id', 0))
    check_date = get_valid_date(params.get('check_date', ''))
    start_date = get_valid_date(params.get('start_date', ''))
    end_date = get_valid_date(params.get('end_date', ''))
    check_month = params.get('check_month', '')

    if check_month != '':
        check_month = get_valid_month(check_month)
        year, month = check_month.split('-')
        start_date, end_date = get_start_end_of_the_month(int(month), int(year))

    group_by = params.get('group_by', '')
    tab = params.get('tab', '')
    project = Project.objects.filter(pk=project_id).first()

    if model in ['VehicleOperationRecord', 'User']:
        display_trashcan = False
    else:
        display_trashcan = True

    context = {
        'page': page,
        'sub_page': sub_page,
        'model': model,
        'project_id': project_id,
        'check_date': check_date if check_date else datetime.now().date().strftime('%Y-%m-%d'),
        'start_date': start_date,
        'end_date': end_date,
        'check_month': check_month,
        'group_by': group_by,
        'tab': tab,
        'lazy_load': params.get('lazy_load', False),
        'display_trashcan':display_trashcan
    }
    if model not in ['VehicleOperationRecord']:
        context['create_new_button_name'] = translate(f'Thêm {model}')
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
    def get_unique_values(records, model_class, field):
        if model_class == StaffData:
            # get driver list from records
            values = records.values_list('driver__full_name', flat=True)
            # get unique values
            contain_data_unique_values = set(values)
            # remove None values
            contain_data_unique_values = [value for value in contain_data_unique_values if value != None]

        elif model_class == VehicleDetail:
            # get vehicle list from records
            values = records.values_list('vehicle', flat=True)
            # get unique values
            contain_data_unique_values = set(values)
            # remove None values
            contain_data_unique_values = [value for value in contain_data_unique_values if value != None]

        # order
        try:
            contain_data_unique_values = sorted(contain_data_unique_values)
        except Exception as e:
            print(e)

        # get all values of the field
        values = model_class.objects.values_list(field, flat=True)
        unique_values = set(values)
        unique_values = [value for value in unique_values if value != None]
        contain_data_unique_values = [value for value in contain_data_unique_values if value in unique_values]

        
        # order
        try:
            unique_values = sorted(unique_values)
        except Exception as e:
            print(e)

        # put contain_data_unique_values in the first of the list
        if contain_data_unique_values:
            unique_values = contain_data_unique_values + [value for value in unique_values if value not in contain_data_unique_values]

        # get param "all" from request
        keyword = request.GET.get('all', None)
        if keyword:
            # keep value which has the keyword
            unique_values = [value for value in unique_values if keyword.lower() in value.lower()]

        # if there is "XE CHẤM CÔNG" in unique_values, remove it, and add it to the top
        if model_class == VehicleDetail:
            if 'XE CHẤM CÔNG' in unique_values:
                unique_values.remove('XE CHẤM CÔNG')   
            unique_values = ['XE CHẤM CÔNG'] + unique_values
            # Don't use vehicle with license plate "72"
            unique_values = [value for value in unique_values if not value.startswith('72')]

        return unique_values

    params = kwargs

    model = params.get('model', '')
    update = params.get('update', False)
    project_id = get_valid_id(params.get('project_id', 0))
    check_date = get_valid_date(params.get('check_date', ''))
    start_date = get_valid_date(params.get('start_date', ''))
    end_date = get_valid_date(params.get('end_date', start_date))
    search_phrase = request.GET.get('all', '')
    filter_vehicle = params.get('filter_vehicle', None)
    if filter_vehicle == "None":
        filter_vehicle = None


    check_month = params.get('check_month', '')
    if check_month != '':
        check_month = get_valid_month(check_month)
        year, month = check_month.split('-')
        start_date, end_date = get_start_end_of_the_month(int(month), int(year))
        # convert to str
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')

    group_by = params.get('group_by', '')
    records = params.get('records', None)


    tab = params.get('tab', '')

    if tab == 'vehicle_operation_data_by_date' or tab == 'driver_salary':
        next = max(1, get_valid_id(params.get('next', None)))
    else:
        next = None

    model_class = globals()[model]
    project = Project.objects.filter(pk=project_id).first()

    if not records:
        # Get the records
        if not project_id:
            records = model_class.objects.all()
        else:
            records = model_class.objects.filter(project=project)
        
        if tab == 'vehicle_revenue' and update=='true':
            records = records.filter(vehicle=filter_vehicle)

        records = filter_records(request, records, model_class, start_date=start_date, end_date=end_date, check_date=check_date, check_month=check_month)

    groups = []
    if group_by:
        GROUPS_PER_PAGE = 5
        # if records.count() == 0:
        #     return '<div id="display-records" class="w-full overflow-scroll"><p class="text-red-600 text-center text-2xl my-10">Không tìm thấy dữ liệu, vui lòng chọn ngày khác</p></div><div up-hungry id="load-more" class="hidden"></div>'
        if model_class == VehicleOperationRecord:
            if group_by == 'vehicle':
                page = next
                next = next + 1
                if not update:
                    group_names = get_unique_values(records, VehicleDetail, 'gps_name')
                else:
                    group_names = [records.first().vehicle]
                if len(group_names) <= page*GROUPS_PER_PAGE:
                    next = "stop"

                page_group_names = group_names[(page-1)*GROUPS_PER_PAGE:page*GROUPS_PER_PAGE]
                for group_name in page_group_names:
                    vehicle = VehicleDetail.objects.filter(gps_name=group_name).first()
                    group_records = records.filter(vehicle=vehicle.gps_name)
                    for record in group_records:
                        record.calculate_working_time()
                    groups.append({
                        'group_id': vehicle.id,
                        'group_name': group_name,
                        'start_time': datetime.strptime(start_date, "%Y-%m-%d").date(),
                        'end_time': datetime.strptime(start_date, "%Y-%m-%d").date(),
                        'drivers': StaffData.objects.filter(position__icontains='driver'),
                        'locations': Location.objects.all(),
                        'records': group_records
                    })
            elif group_by == 'driver':
                page = next
                next = next + 1
                if not update:
                    group_names = get_unique_values(records, StaffData, 'full_name')
                else:
                    group_names = [records.first().driver.full_name]

                if len(group_names) <= page*GROUPS_PER_PAGE:
                    next = "stop"

                page_group_names = group_names[(page-1)*GROUPS_PER_PAGE:page*GROUPS_PER_PAGE]
                for group_name in page_group_names:
                    driver = StaffData.objects.filter(full_name=group_name).first()
                    group_records = records.filter(driver=driver)

                    groups.append({
                        'group_id': driver.id,
                        'group_name': group_name,
                        'start_time': datetime.strptime(start_date, "%Y-%m-%d").date(),
                        'end_time': datetime.strptime(start_date, "%Y-%m-%d").date(),
                        'drivers': StaffData.objects.filter(position__icontains='driver'),
                        'locations': Location.objects.all(),
                        'records': group_records
                    })

    
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

    elif model_class == PaymentRecord:
        for record in records:
            if record.requested_amount == 0:
                record.requested_amount = "chưa đề nghị"
                record.requested_date = ""

            if record.transferred_amount == 0:
                record.transferred_amount = "chưa thanh toán"
                record.payment_date = ""

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
               'start_date': start_date,
               'end_date': end_date,
               'check_month': check_month,    
               'tab': tab,
               'next': next,
               'search_phrase': search_phrase,
               'vehicle': filter_vehicle
    }

    html = render_to_string(template, context, request)
    return html




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
        'model_class': model_class,
        'project_id': project_id,
        'modal': modal,
        'form': form,
        'record': record
    }

    if model in ['VehicleMaintenance', 'SupplyOrder']:
        permissions = request.user.check_permission('VehicleMaintenance')
        context['permissions'] = permissions

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
    # Get monday and sunday dates of the week that contains check_date
    monday = check_date - timedelta(days=check_date.weekday())
    sunday = check_date + timedelta(days=6 - check_date.weekday())
    last_sunday = sunday - timedelta(days=7)
    week = f'{monday.strftime("%d-%m-%Y")} đến {sunday.strftime("%d-%m-%Y")}'
    jobplans_in_week = JobPlan.objects.filter(start_date__gte=monday, end_date__lte=sunday, job__project=project)
    job_date_reports = JobDateReport.objects.filter(date=check_date, job__project=project)

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
               'project_id': project_id,
               'project': project}

    return render_to_string(template, context, request)


