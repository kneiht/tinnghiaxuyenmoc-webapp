
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
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

class JobDateReportAdmin(admin.ModelAdmin):
    list_display = ('job', 'date', 'quantity', 'note', 'created_at')
    list_filter = ('created_at', 'job')
    search_fields = ('job__name', 'note')

class DataVehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_type', 'license_plate', 'vehicle_name', 'gps_name', 'vehicle_inspection_number', 'vehicle_inspection_due_date', 'created_at')
    list_filter = ('created_at', 'vehicle_type')
    search_fields = ('license_plate', 'vehicle_name', 'gps_name')

class DataDriverAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'hire_date', 'identity_card', 'birth_year', 'status', 'created_at')
    list_filter = ('created_at', 'status')
    search_fields = ('full_name', 'identity_card', 'birth_year')


class DataVehicleTypeDetailAdmin(admin.ModelAdmin):
    list_display = ('vehicle_type', 'vehicle_type_detail', 'revenue_per_8_hours', 'oil_consumption_per_hour', 'lubricant_consumption', 'insurance_fee', 'road_fee_inspection', 'tire_wear', 'police_fee', 'created_at')
    list_filter = ('created_at', 'vehicle_type')
    search_fields = ('vehicle_type', 'vehicle_type_detail')



class JobPlanAdmin(admin.ModelAdmin):
    list_display = ('job', 'start_date', 'end_date', 'plan_quantity', 'note', 'created_at')
    list_filter = ('created_at', 'job')
    search_fields = ('job__name', 'note')



class UserExtraAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'avatar', 'settings', 'created_at')
    list_filter = ('created_at', 'role')
    search_fields = ('user__username', 'role')


class VehicleOperationRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'start_time', 'end_time', 'duration_seconds', 'source', 'driver', 'image')
    search_fields = ('vehicle', 'driver__full_name')
    raw_id_fields = ('driver',)

admin.site.register(VehicleOperationRecord, VehicleOperationRecordAdmin)

admin.site.register(UserExtra, UserExtraAdmin)


admin.site.register(JobPlan, JobPlanAdmin)
admin.site.register(DataVehicleTypeDetail, DataVehicleTypeDetailAdmin)

admin.site.register(JobDateReport, JobDateReportAdmin)
admin.site.register(DataVehicle, DataVehicleAdmin)
admin.site.register(DataDriver, DataDriverAdmin)

admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectUser, ProjectUserAdmin)
admin.site.register(Job, JobAdmin)