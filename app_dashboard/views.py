# security issues
# https://chat.openai.com/share/16295269-0f56-4c6a-8cd7-7ea903fdaf86
# cần check truy cập trang cần đúng school_id and user


import time, datetime, os, json

from io import BytesIO
import pandas as pd
from sqlalchemy import create_engine
from django.db import connection

from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect

from django.http import HttpResponse, HttpResponseForbidden, JsonResponse


from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

from django.views import View
from .html_render import html_render

from .models import Project, ProjectUser
from .forms import ProjectForm

def is_admin(user):
    # check if there is no user => allow to upload db
    if User.objects.count() == 0:
        return True
    else:
        return user.is_authenticated and user.is_active and user.is_staff and user.is_superuser

def is_project_user(request, project_id):
    project = Project.objects.filter(pk=project_id).first()
    project_user = ProjectUser.objects.filter(project=project, user=request.user).first()
    if project_user:
        return True
    else:
        return False


# GENERAL PAGES ==============================================================
def create_display(request, context):
    return render(request, 'pages/project.html', context)


def create_form(request, model_class, pk):
    return "create form for "

@login_required
def project(request):
    model_class = Project
    user = request.user
    records = model_class.objects.filter(users=user)
    context = {'title': "Trang quản lý các dự án", 'records': records}
    return create_display(request, context)

    


# DATABASE MANAGEMENT VIEWS ===================================================

# def create_display(request, model):
#     return "create display"

#     if model == 'Project':
#         user = request.user
#         records = model.objects.filter(users=user)
#     else:
#         records = model.objects.all()

#     # Determine the fields to be used as filter options\
#     fields = ['all', 'name', 'description']
    
#     # Get all query parameters except 'sort' as they are assumed to be field filters
#     query_params = {k: v for k, v in request.GET.lists() if k != 'sort'}
#     if not query_params:
#         # Filter Discontinued and Archived
#         if hasattr(self.model_class, 'status'):
#             records = records.exclude(status__in=['discontinued', 'archived'])
            
#     else:
#         # Construct Q objects for filtering
#         combined_query = Q()
#         if 'all' in query_params:
#             specified_fields = fields[1:]  # Exclude 'all' to get the specified fields
#             all_fields_query = Q()
#             for value in query_params['all']:
#                 for specified_field in specified_fields:
#                     if specified_field in [field.name for field in self.model_class._meta.get_fields()]:
#                         all_fields_query |= Q(**{f"{specified_field}__icontains": value})
#             combined_query &= all_fields_query
#         else:
#             for field, values in query_params.items():
#                 if field in fields:
#                     try:
#                         self.model_class._meta.get_field(field)
#                         field_query = Q()
#                         for value in values:
#                             field_query |= Q(**{f"{field}__icontains": value})
#                         combined_query &= field_query
#                     except FieldDoesNotExist:
#                         print(f"Ignoring invalid field: {field}")

#         # Filter records based on the query
#         records = records.filter(combined_query)

#     context = {
#         'select': self.page, 
#         'title': self.title, 
#         'records': records,
#         'fields':  fields,
#         'school': School.objects.filter(pk=school_id).first() if school_id and school_id != "all" else School.objects.filter(pk=1).first()
#     }

#     return render(request, 'pages/single_page.html', context)







# DATABASE OPERATIONS ==============================================================
def delete_all_rows(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM {table_name};")


def insert_rows_using_to_sql(df, table_name):
    db_engine = settings.DATABASES['default']['ENGINE']
    db_name = settings.DATABASES['default']['NAME']
    user = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    host = settings.DATABASES['default']['HOST']
    port = settings.DATABASES['default']['PORT']

    if 'mysql' in db_engine:
        # MySQL database
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}")
    elif 'sqlite' in db_engine:
        # SQLite database
        engine = create_engine(f"sqlite:///{db_name}")
    else:
        # Add other database engines as needed
        raise NotImplementedError("Database engine not supported")

    # Write the DataFrame to the database table using df.to_sql
    columns_to_keep = [col for col in df.columns if "exclude" not in col]
    df_filtered = df[columns_to_keep]
    
    df_filtered.to_sql(table_name, con=engine, if_exists='append', index=False)


def reset_primary_key(table_name):
    # Check the database engine
    if 'postgresql' in connection.settings_dict['ENGINE']:
        sql = f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1;"
    elif 'mysql' in connection.settings_dict['ENGINE']:
        sql = f"ALTER TABLE {table_name} AUTO_INCREMENT = 1;"
    elif 'sqlite3' in connection.settings_dict['ENGINE']:
        # SQLite does not support altering the AUTOINCREMENT value.
        return
    else:
        raise ValueError("Unsupported database backend")

    with connection.cursor() as cursor:
        cursor.execute(sql)


def get_table_names():
    #print('\n\n', connection.vendor)
    # Get a list of all table names for the current database
    if connection.vendor == 'mysql':
        # For MySQL
        table_names = connection.introspection.table_names()
    elif connection.vendor == 'sqlite':
        # For SQLite
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]  # Exclude internal SQLite table
    else:
        # Handle other databases here
        table_names = []

    return table_names


def fetch_table_data(table_name):
    # Fetch data from the specified table
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    data = pd.DataFrame(rows, columns=columns)
    return data



@user_passes_test(is_admin)
def db_backup(request):
    return render(request, 'pages/db_backup.html')



@user_passes_test(is_admin)
def download_db_backup(request):
    # Get a list of all table names for the current database
    if connection.vendor == 'mysql':
        # Get list of all tables in the database
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            table_names = [row[0] for row in cursor.fetchall()]
    elif connection.vendor == 'sqlite':
        # Get list of all tables in the database for SQLite
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_names = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]  # Exclude internal SQLite table
    else:
        # Handle other databases here
        table_names = []

    # Create a Pandas Excel writer using XlsxWriter as the engine
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Loop through tables and write each to a separate sheet
        for table_name in table_names:
            data = fetch_table_data(table_name)
            # Shorten the table name for the Excel sheet
            shortened_table_name = table_name.replace('app_dashboard_', '')
            data.to_excel(writer, sheet_name=shortened_table_name, index=False)

    # Get the Excel file
    excel_data = output.getvalue()

    # Return the Excel file as an HTTP response
    response = HttpResponse(
        excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    # name the db based on time
    filename = f"db_{datetime.datetime.now().strftime('%Y_%m_%d')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response





@user_passes_test(is_admin)
def upload_db_backup(request):
    if request.method == 'GET':
        return "API này không dùng GET"

    if request.method == 'POST':
        excel_file = request.FILES.get('file')
        table_name_origin = request.POST.get('table_name')

        if excel_file and excel_file.name.endswith('.xlsx'):
            if table_name_origin=='all':
                table_list = [
                    #'auth_user',
                    'timeframe',
                    'thumbnail',
                    'school',
                    'schooluser',
                    'filtervalues',
                    'class',
                    'student',
                    'studentclass',
                    
                    'attendance',
                    'financialtransaction',
                ]
                table_list_reverse = list(table_list)
                table_list_reverse.reverse()

            else:
                table_list = [table_name_origin]
                table_list_reverse = list(table_list)
                table_list_reverse.reverse()


            for table_name in table_list_reverse:
                sql_table_name = 'app_dashboard_' + table_name if table_name != 'auth_user' else table_name
                try:
                    # Delete all current rows from the table
                    delete_all_rows(sql_table_name)
                    reset_primary_key(sql_table_name)
                except Exception as e:
                    return JsonResponse({'error': str(e), 'table': sql_table_name, 'delete':'delete'})


            for table_name in table_list:
                try:
                    # Read the Excel file into a DataFrame
                    df = pd.read_excel(excel_file, sheet_name=table_name)
                    sql_table_name = 'app_dashboard_' + table_name if table_name != 'auth_user' else table_name
                    # Insert new rows into the specified table using df.to_sql
                    insert_rows_using_to_sql(df, sql_table_name)

                except Exception as e:
                    return JsonResponse({'error': str(e), 'table': sql_table_name, 'update':'update'})
            return JsonResponse({'message': 'Data updated successfully'})
        else:
            return JsonResponse({'error': 'Please upload a valid Excel file (xlsx)'})

    return JsonResponse({'error': 'Invalid request'})





