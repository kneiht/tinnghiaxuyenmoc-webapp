from django.contrib import admin

from .models.models import *


@admin.register(UserExtra)
class UserExtraAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'role')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'due_date', 'created_at')
    list_filter = ('due_date',)
    search_fields = ('name', 'description')


@admin.register(TaskUser)
class TaskUserAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'created_at')
    search_fields = ('task__name', 'user__username')
    list_filter = ('created_at',)


@admin.register(Thumbnail)
class ThumbnailAdmin(admin.ModelAdmin):
    list_display = ('reference_url', 'thumbnail')
    search_fields = ('reference_url',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    ordering = ('name',)



@admin.register(ProjectUser)
class ProjectUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'created_at')
    list_filter = ('role', 'project')
    search_fields = ('user__username', 'project__name')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'quantity', 'unit_price', 'total_amount', 'start_date', 'end_date')
    list_filter = ('status', 'category', 'start_date', 'end_date')
    search_fields = ('name', 'category', 'project__name')
    ordering = ('category', 'secondary_id')


@admin.register(JobPlan)
class JobPlanAdmin(admin.ModelAdmin):
    list_display = ('job', 'status', 'plan_quantity', 'plan_amount', 'start_date', 'end_date', 'created_at')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('job__name', 'job__project__name')


@admin.register(JobDateReport)
class JobDateReportAdmin(admin.ModelAdmin):
    list_display = ('job', 'date', 'quantity', 'date_amount', 'material', 'labor', 'created_at')
    list_filter = ('date',)
    search_fields = ('job__name', 'material', 'labor')


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('vehicle_type', 'note', 'created_at')
    search_fields = ('vehicle_type', 'note')
    ordering = ('vehicle_type',)


@admin.register(StaffData)
class StaffDataAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'status', 'hire_date', 'phone_number', 'address')
    list_filter = ('position', 'status', 'hire_date')
    search_fields = ('full_name', 'identity_card', 'phone_number', 'address')
    ordering = ('full_name',)
    fieldsets = (
        ("Personal Information", {
            'fields': ('full_name', 'birth_year', 'identity_card', 'phone_number', 'address', 'hire_date')
        }),
        ("Work Information", {
            'fields': ('position', 'status')
        }),
        ("Bank Information", {
            'fields': ('bank_name', 'account_number', 'account_holder_name')
        }),
    )

@admin.register(VehicleRevenueInputs)
class VehicleRevenueInputsAdmin(admin.ModelAdmin):
    list_display = ('vehicle_type', 'note', 'created_at')
    list_filter = ('vehicle_type',)
    search_fields = ('vehicle_type__name',)
    ordering = ('vehicle_type',)



@admin.register(DriverSalaryInputs)
class DriverSalaryInputsAdmin(admin.ModelAdmin):
    list_display = ('driver', 'basic_month_salary', 'calculation_method', 'valid_from')
    list_filter = ('calculation_method', 'valid_from')
    search_fields = ('driver__full_name', 'vehicle_type__name')
    ordering = ('driver',)



# Admin for VehicleDetail
@admin.register(VehicleDetail)
class VehicleDetailAdmin(admin.ModelAdmin):
    list_display = VehicleDetail.get_display_fields()
    search_fields = ['license_plate', 'vehicle_name', 'gps_name']
    list_filter = ['vehicle_type']
    ordering = ['created_at']

# Admin for DumbTruckPayRate
@admin.register(DumbTruckPayRate)
class DumbTruckPayRateAdmin(admin.ModelAdmin):
    list_display = DumbTruckPayRate.get_display_fields()
    search_fields = ['xe__license_plate', 'xe__vehicle_name']
    list_filter = ['xe__vehicle_type']

# Admin for DumbTruckRevenueData
@admin.register(DumbTruckRevenueData)
class DumbTruckRevenueDataAdmin(admin.ModelAdmin):
    list_display = DumbTruckRevenueData.get_display_fields()
    search_fields = ['loai_chay', 'kich_co_xe']
    list_filter = ['loai_chay', 'cach_tinh', 'loai_vat_tu', 'moc', 'kich_co_xe']

# Admin for Location
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = Location.get_display_fields()
    search_fields = ['name', 'address']
    list_filter = ['type_of_location']

# Admin for NormalWorkingTime
@admin.register(NormalWorkingTime)
class NormalWorkingTimeAdmin(admin.ModelAdmin):
    list_display = NormalWorkingTime.get_display_fields()
    list_filter = ['valid_from']
    ordering = ['-valid_from']

# Admin for Holiday
@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = Holiday.get_display_fields()
    search_fields = ['note']
    list_filter = ['date']
    ordering = ['-date']

# Admin for VehicleOperationRecord
# @admin.register(VehicleOperationRecord)
# class VehicleOperationRecordAdmin(admin.ModelAdmin):
#     list_display = VehicleOperationRecord.get_display_fields()
#     search_fields = ['vehicle', 'driver__full_name', 'location__name']
#     list_filter = ['source', 'driver', 'location']
#     ordering = ['-start_time']



# Register your models here.

@admin.register(VehicleDepreciation)
class VehicleDepreciationAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'depreciation_amount', 'from_date', 'to_date', 'note')
    search_fields = ('vehicle__name', 'from_date', 'to_date')
    list_filter = ('from_date', 'to_date')
    ordering = ('-from_date',)

@admin.register(VehicleBankInterest)
class VehicleBankInterestAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'interest_amount', 'from_date', 'to_date', 'note')
    search_fields = ('vehicle__name', 'from_date', 'to_date')
    list_filter = ('from_date', 'to_date')
    ordering = ('-from_date',)

@admin.register(VehicleMaintenance)
class VehicleMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'maintenance_amount', 'from_date', 'to_date', 'note')
    search_fields = ('vehicle__name', 'from_date', 'to_date')
    list_filter = ('from_date', 'to_date')
    ordering = ('-from_date',)

@admin.register(RepairPart)
class RepairPartAdmin(admin.ModelAdmin):
    list_display = ('vehicle_type', 'part_number', 'part_name', 'part_price', 'valid_from')
    search_fields = ('part_number', 'part_name')
    list_filter = ('vehicle_type', 'valid_from')
    ordering = ('-valid_from',)

@admin.register(VehicleMaintenanceRepairPart)
class VehicleMaintenanceRepairPartAdmin(admin.ModelAdmin):
    list_display = ('vehicle_maintenance', 'repair_part', 'quantity')
    search_fields = ('vehicle_maintenance__vehicle__name', 'repair_part__part_name')
    ordering = ('-vehicle_maintenance__from_date',)




@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle_maintenance', 'provider', 'status', 'lock', 'purchase_amount',
                    'previous_debt', 'requested_amount', 'requested_date', 'transferred_amount',
                    'payment_date', 'money_source', 'debt', 'note', 'image1')
    search_fields = ('vehicle_maintenance__vehicle__name', 'provider__name', 'status')
    list_filter = ('status', 'money_source', 'payment_date')
    ordering = ('-payment_date',)


@admin.register(PartProvider)
class PartProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'bank_name', 'account_number', 'account_holder_name', 'total_purchase_amount',
                    'total_transferred_amount', 'total_outstanding_debt', 'phone_number', 'address', 'note')
    search_fields = ('name', 'bank_name', 'account_number', 'account_holder_name')
    list_filter = ('total_purchase_amount', 'total_transferred_amount', 'total_outstanding_debt')
    ordering = ('-created_at',)
