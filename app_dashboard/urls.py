
from . import views, views_backup, views_components
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


    path('api/load-form/<str:model>/<int:pk>', views.load_form, name='load_form'),
    path('api/handle-form/<str:model>/<int:pk>', views.handle_form, name='handle_form'),



    path('api/load-content/<str:page>/<str:model>', views.load_content, name='load_content'),
    path('api/load-content/<str:page>/<str:model>/<int:project_id>', views.load_content, name='load_content_with_project'),
    


    # Test components
    path('api/render_title_bar/<str:page>/<str:model>/', views_components.render_title_bar, name='render_title_bar'),


    path('api/download-project/<int:pk>/', views.download_project, name='download_project'),
    path('api/upload-project/<int:pk>/', views.upload_project, name='upload_project'),

    path('api/update-project-progress/<int:pk>/', views.update_project_progress, name='update_project_progress'),

]