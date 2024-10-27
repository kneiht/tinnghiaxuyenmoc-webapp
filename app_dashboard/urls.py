
from . import views, views_backup
from django.urls import re_path, path


# If pk==0 -> create new record

urlpatterns = [
    # DATABASE UPLOAD AND DOWNLOAD
    path('db-backup/', views_backup.db_backup, name='db_backup'),
    path('download-db-backup/', views_backup.download_db_backup, name='download_db_backup'),
    path('upload-db-backup/', views_backup.upload_db_backup, name='upload_db_backup'),

    path('', views.page_projects, name='home'),
    
    path('projects', views.page_projects, name='page_projects'),
    path('projects/<int:pk>/', views.page_each_project, name='page_each_project'),
    path('manage-data/', views.page_manage_data, name='page_manage_data'),
    path('transport-department/', views.page_transport_department, name='page_transport_department'),

    path('api/load-form/<str:model>/<int:pk>', views.load_form, name='load_form'),
    path('api/handle-form/<str:model>/<int:pk>', views.handle_form, name='handle_form'),

    path('api/load-content/<str:page>/<str:model>', views.load_content, name='load_content'),
    path('api/load-content/<str:page>/<str:model>/<int:project_id>', views.load_content, name='load_content_with_project'),
    path('api/load-element/<str:element>/', views.load_element, name='load_element'),
    

    path('api/load-weekplan-table/<int:project_id>/', views.load_weekplan_table, name='load_weekplan_table'),
    path('api/handle-weekplan-form/', views.handle_weekplan_form, name='handle_weekplan_form'),
    path('api/handle-date-report-form/', views.handle_date_report_form, name='handle_date_report_form'),


    path('api/gantt-chart-data/<int:project_id>/', views.get_gantt_chart_data, name='get_gantt_chart_data'),


    path('api/download-excel-template/<str:template_name>', views.download_excel_template, name='download_excel_template'),
    path('api/upload-project/<int:project_id>/', views.upload_project, name='upload_project'),
    
]