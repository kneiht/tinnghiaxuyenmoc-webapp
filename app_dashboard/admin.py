
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Project,
    ProjectUser,
    Job
)
from django.utils.safestring import mark_safe
from django import forms


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image', 'created_at', 'start_date', 'end_date')
    list_filter = ('created_at', 'start_date', 'end_date')
    search_fields = ('name', 'description')

class ProjectUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'created_at')
    list_filter = ('created_at', 'role')
    search_fields = ('user__username', 'project__name', 'role')

class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'project', 'created_at')
    list_filter = ('created_at', 'project')
    search_fields = ('name', 'description', 'project__name')



admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectUser, ProjectUserAdmin)
admin.site.register(Job, JobAdmin)