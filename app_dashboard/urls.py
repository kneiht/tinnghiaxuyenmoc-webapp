
from . import views, views_backup
from django.urls import re_path, path


# If pk==0 -> create new record

urlpatterns = [
    # DATABASE UPLOAD AND DOWNLOAD
    path('db-backup/', views_backup.db_backup, name='db_backup'),
    path('download-db-backup/', views_backup.download_db_backup, name='download_db_backup'),
    path('upload-db-backup/', views_backup.upload_db_backup, name='upload_db_backup'),

    path('', views.page_home, name='page_home'),
    path('home', views.page_home, name='page_home'),
    path('home/<str:sub_page>/', views.page_home, name='page_home'),
    
    path('projects', views.page_projects, name='page_projects'),
    path('projects/<int:pk>/', views.page_each_project, name='page_each_project'),

    path('general-data/', views.page_general_data, name='page_general_data'),
    path('general-data/<str:sub_page>/', views.page_general_data, name='page_general_data'),


    path('transport-department/', views.page_transport_department, name='page_transport_department'),
    path('transport-department/<str:sub_page>/', views.page_transport_department, name='page_transport_department'),


    path('api/handle-form/<str:model>/<int:pk>', views.handle_form, name='handle_form'),

    path('api/load-elements', views.load_elements, name='load_elements'),
    path('api/gantt-chart-data/<int:project_id>/', views.get_gantt_chart_data, name='get_gantt_chart_data'),

    
    path('api/load-weekplan-table/<int:project_id>/', views.load_weekplan_table, name='load_weekplan_table'),
    path('api/handle-weekplan-form/', views.handle_weekplan_form, name='handle_weekplan_form'),
    path('api/handle-date-report-form/', views.handle_date_report_form, name='handle_date_report_form'),
    path('api/handle-vehicle-operation-form/', views.handle_vehicle_operation_form, name='handle_vehicle_operation_form'),



    path('api/save-vehicle-operation-record', views.save_vehicle_operation_record, name='save_vehicle_operation_record'),
    path('api/get_vehicle_list_from_binhanh', views.get_vehicle_list_from_binhanh, name='get_vehicle_list_from_binhanh'),
    path('api/get_trip_data_from_binhanh', views.get_trip_data_from_binhanh, name='get_trip_data_from_binhanh'),
    
    path('api/form_repair_parts', views.form_repair_parts, name='form_repair_parts'),
    path('api/form_maintenance_images/<int:maintenance_id>/', views.form_maintenance_images, name='form_maintenance_images'),
    path('api/form_maintenance_payment_request', views.form_maintenance_payment_request, name='form_maintenance_payment_request'),


    path('test', views.test, name='test'),


    path('api/download-excel-template/<str:template_name>', views.download_excel_template, name='download_excel_template'),
    path('api/upload-project/<int:project_id>/', views.upload_project, name='upload_project'),
    

    path('api/db_table/', views_backup.db_table, name='db_table'),

]