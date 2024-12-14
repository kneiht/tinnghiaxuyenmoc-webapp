
from django import forms
from datetime import datetime
from django.shortcuts import get_object_or_404


from django.db.models import Exists, OuterRef

from .models import *


from django.core.exceptions import ValidationError


def validate_username_length(value, min_length=6):
    if len(value) < min_length:  # 7 because it should be more than 6 characters
        raise ValidationError('Tên tài khoản phải dài ít nhất 7 ký tự')



class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'status', 'image', 'func_source', 'description', 'start_date', 'end_date']

    
        labels = {
            'name': 'Tên dự án',
            'status': 'Trạng thái',
            'func_source': 'Nguồn vốn',
            'description': 'Mô tả',
            'image': 'Hình ảnh',
            'start_date': 'Ngày bắt đầu',
            'end_date': 'Ngày kết thúc',
        }
    
        widgets = {
            'name': forms.TextInput(attrs={
                    'placeholder': 'Nhập tên dự án',
                    'required': 'required',
                    'class': 'form-input'}),
            'func_source': forms.TextInput(attrs={
                    'placeholder': 'Nhập nguồn vốn',
                    'required': 'required',
                    'class': 'form-input'}),

            'status': forms.Select(attrs={
                    'class': 'form-input'}),
            'description': forms.Textarea(attrs={
                    'class': 'form-input h-20', 
                    'rows': 2}),
            'image': forms.FileInput(attrs={
                    'class': 'form-input-file',}),
            'start_date': forms.DateInput(attrs={
                    'class': 'form-input',
                    'type': 'date'}),
            'end_date': forms.DateInput(attrs={
                    'class': 'form-input',
                    'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError('Ngày bắt đầu phải nhỏ hoặc bằng ngày kết thúc.')
        return cleaned_data


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['project', 'name', 'status', 'category', 'unit', 'unit_price', 'quantity', 'start_date', 'end_date', 'description']

        labels = {
            'status': 'Trạng thái',
            'name': 'Tên công việc',
            'category': 'Danh mục',
            'unit': 'Đơn vị',
            'unit_price': 'Đơn giá',
            'quantity': 'Khối lượng',
            'description': 'Mô tả',
            'start_date': 'Ngày bắt đầu',
            'end_date': 'Ngày kết thúc',
        }
    
        widgets = {
            'status': forms.Select(attrs={
                    'class': 'form-input'}),
            'name': forms.TextInput(attrs={
                    'placeholder': 'Nhập tên công việc',
                    'required': 'required',
                    'class': 'form-input'}),
            'category': forms.TextInput(attrs={
                    'placeholder': 'Loại công việc',
                    'class': 'form-input'}),
            'unit': forms.TextInput(attrs={
                    'placeholder': 'Đơn vị',
                    'required': 'required',
                    'class': 'form-input'}),

            'unit_price': forms.NumberInput(attrs={
                    'placeholder': 'Đơn giá',
                    'class': 'form-input'}),

            'quantity': forms.NumberInput(attrs={
                    'placeholder': 'Khối lượng',
                    'class': 'form-input'}),
            'description': forms.Textarea(attrs={
                    'class': 'form-input h-20', 
                    'rows': 2}),
            'start_date': forms.DateInput(attrs={
                    'class': 'form-input',
                    'required': 'required',
                    'type': 'date'}),
            'end_date': forms.DateInput(attrs={
                    'class': 'form-input',
                    'required': 'required',
                    'type': 'date'}),
        }



class JobPlanForm(forms.ModelForm):
    class Meta:
        model = JobPlan
        fields = ['job', 'plan_quantity', 'start_date', 'end_date']
        labels = {
            'job': 'Công việc',
            'quantity': 'Khối lượng',
            'start_date': 'Ngày bắt đầu',
            'end_date': 'Ngày kết thúc',
            'status': 'Trạng thái',
        }
        widgets = {
            'job': forms.Select(attrs={
                    'class': 'form-input'}),
            'plan_quantity': forms.NumberInput(attrs={
                    'placeholder': 'Số lượng',
                    'class': 'form-input'}),
            'start_date': forms.DateInput(attrs={
                    'class': 'form-input',
                    'type': 'date'}),
            'end_date': forms.DateInput(attrs={
                    'class': 'form-input',
                    'type': 'date'}),
        }



class VehicleTypeForm(forms.ModelForm):
    class Meta:
        model = VehicleType
        fields = ['vehicle_type', 'note']
        labels = {
            'vehicle_type': 'Loại xe',
            'note': 'Ghi chú',
        }
        widgets = {
            'vehicle_type': forms.TextInput(attrs={
                    'placeholder': 'Loại xe (điền chi tiết như "Xe ben 15 tấn")',
                    'class': 'form-input'}),
            'note': forms.Textarea(attrs={
                    'class': 'form-input',
                    'rows': 2}),
        }





class VehicleRevenueInputsForm(forms.ModelForm):
    class Meta:
        model = VehicleRevenueInputs
        fields = [
            'vehicle_type', 'revenue_day_price', 'number_of_hours',
            'oil_consumption_liters_per_hour', 'oil_consumption_per_hour',
            'lubricant_consumption', 'insurance_fee', 'road_fee_inspection',
            'tire_wear', 'police_fee', 'note', 'valid_from'
        ]
        labels = {
            'vehicle_type': 'Loại xe',
            'revenue_per_8_hours': 'Đơn giá doanh thu/8 tiếng',
            'oil_consumption_per_hour': 'Định mức dầu 1 tiếng',
            'lubricant_consumption': 'Định mức nhớt',
            'insurance_fee': 'Định mức bảo hiểm',
            'road_fee_inspection': 'Định mức sử dụng đường bộ/Đăng kiểm',
            'tire_wear': 'Định mức hao mòn lốp xe',
            'police_fee': 'Định mức CA'
        }


        labels = {
            'vehicle_type': 'Loại xe',
            'revenue_day_price': 'Đơn giá doanh thu',
            'number_of_hours': 'Số giờ tính doanh thu',
            'oil_consumption_liters_per_hour': 'Số lít dầu 1 tiếng',
            'oil_consumption_per_hour': 'Định mức dầu 1 tiếng',
            'lubricant_consumption': 'Định mức nhớt',
            'insurance_fee': 'Định mức bảo hiểm',
            'road_fee_inspection': 'Định mức sử dụng đường bộ/Đăng kiểm',
            'tire_wear': 'Định mức hao mòn lốp xe',
            'police_fee': 'Định mức CA',
            'valid_from': 'Ngày bắt đầu áp dụng',
            'note': 'Ghi chú'
        }

        widgets = {
            'vehicle_type': forms.Select(attrs={
                'class': 'form-input',
                'required': 'required'
            }),
            'revenue_day_price': forms.NumberInput(attrs={
                'placeholder': 'Nhập đơn giá doanh thu',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'number_of_hours': forms.NumberInput(attrs={
                'placeholder': 'Nhập số giờ tính doanh thu',
                'class': 'form-input',
                'required': 'required'
            }),
            'oil_consumption_liters_per_hour': forms.NumberInput(attrs={
                'placeholder': 'Nhập số lít dầu 1 tiếng',
                'class': 'form-input',
                'required': 'required'
            }),
            'oil_consumption_per_hour': forms.NumberInput(attrs={
                'placeholder': 'Nhập định mức dầu 1 tiếng',
                'class': 'form-input',
                'required': 'required'
            }),
            'lubricant_consumption': forms.NumberInput(attrs={
                'placeholder': 'Nhập định mức nhớt',
                'class': 'form-input',
                'required': 'required'
            }),
            'insurance_fee': forms.NumberInput(attrs={
                'placeholder': 'Nhập định mức bảo hiểm',
                'class': 'form-input',
                'required': 'required'
            }),
            'road_fee_inspection': forms.NumberInput(attrs={
                'placeholder': 'Nhập định mức sử dụng đường bộ/Đăng kiểm',
                'class': 'form-input',
                'required': 'required'
            }),
            'tire_wear': forms.NumberInput(attrs={
                'placeholder': 'Nhập định mức hao mòn lốp xe',
                'class': 'form-input',
                'required': 'required'
            }),
            'police_fee': forms.NumberInput(attrs={
                'placeholder': 'Nhập định mức CA',
                'class': 'form-input',
                'required': 'required'
            }),
            'valid_from': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'required': 'required'
            }),
            'note': forms.TextInput(attrs={
                'placeholder': 'Nhập ghi chú',
                'class': 'form-input'
            })
        }




class VehicleDetailForm(forms.ModelForm):
    class Meta:
        model = VehicleDetail
        fields = ['vehicle_type', 'license_plate', 'vehicle_name', 'gps_name', 
        'vehicle_inspection_number', 'vehicle_inspection_due_date']

        labels = {
            'vehicle_type': 'Loại xe',
            'license_plate': 'Biển kiểm soát',
            'vehicle_name': 'Tên nhận dạng xe',
            'gps_name': 'Tên trên định vị',
            'vehicle_inspection_number': 'Số đăng kiểm',
            'vehicle_inspection_due_date': 'Thời hạn đăng kiểm',
        }
    
        widgets = {
            'vehicle_type': forms.Select(attrs={
                    'class': 'form-input'}),
            'license_plate': forms.TextInput(attrs={
                    'placeholder': 'Nhập biển kiểm soát xe',
                    'required': 'required',
                    'class': 'form-input'}),
            'vehicle_name': forms.TextInput(attrs={
                    'placeholder': 'Tên nhận dạng xe',
                    'class': 'form-input'}),
            'gps_name': forms.TextInput(attrs={
                    'placeholder': 'Tên trên định vị',
                    'class': 'form-input'}),
            'vehicle_inspection_number': forms.TextInput(attrs={
                    'placeholder': 'Số đăng kiểm',
                    'class': 'form-input'}),
            'vehicle_inspection_due_date': forms.DateInput(attrs={
                    'class': 'form-input',
                    'type': 'date'}),
        }


class StaffDataForm(forms.ModelForm):
    class Meta:
        model = StaffData
        fields = [
            'full_name', 'status', 
            'position',  'hire_date',
            'identity_card', 'birth_year',
            'bank_name', 'account_number',
            'account_holder_name',
            'phone_number', 'address',
        ]
        
        labels = {
            'full_name': 'Họ và tên',
            'status': 'Trang thái',
            'position': 'Chức vụ',
            'hire_date': 'Ngày vào làm',
            'identity_card': 'CCCD',
            'birth_year': 'Ngày sinh',
            'bank_name': 'Ngân hàng',
            'account_number': 'Số tài khoản',
            'account_holder_name': 'Tên chủ tài khoản',
            'phone_number': 'Số điện thoại',
            'address': 'Địa chỉ',
        }

        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Nhập họ và tên',
                'class': 'form-input',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-input',
                'required': 'required'
            }),
            'position': forms.Select(attrs={
                'class': 'form-input',
                'required': 'required'
            }),

            'hire_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'required': 'required'
            }),
            'identity_card': forms.TextInput(attrs={
                'placeholder': 'Nhập CCCD',
                'class': 'form-input',
                'required': 'required'
            }),
            'birth_year': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
                'required': 'required'
            }),
            'bank_name': forms.TextInput(attrs={
                'placeholder': 'Nhập tên ngân hàng',
                'class': 'form-input',
            }),
            'account_number': forms.TextInput(attrs={
                'placeholder': 'Nhập số tài khoản',
                'class': 'form-input',
            }),
            'account_holder_name': forms.TextInput(attrs={
                'placeholder': 'Nhập tên chủ tài khoản',
                'class': 'form-input',
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Nhập số điện thoại',
                'class': 'form-input',
                'required': 'required'
            }),
            'address': forms.TextInput(attrs={
                'placeholder': 'Nhập địa chỉ',
                'class': 'form-input',
                'required': 'required'
            }),
        }




from django import forms
from .models import DriverSalaryInputs

class DriverSalaryInputsForm(forms.ModelForm):
    class Meta:
        model = DriverSalaryInputs
        fields = [
            'driver', 'calculation_method',
            'basic_month_salary', 'sunday_month_salary_percentage', 'holiday_month_salary_percentage', 
            'normal_hourly_salary', 'normal_overtime_hourly_salary', 'sunday_hourly_salary', 
            'sunday_overtime_hourly_salary', 'holiday_hourly_salary', 'holiday_overtime_hourly_salary', 
            'trip_salary', 'fixed_allowance', 'insurance_amount',
            'valid_from', 'note'
        ]

        labels = {
            'driver': 'Tài xế',
            'calculation_method': 'Cách tính',
            'basic_month_salary': 'Lương cơ bản tháng',
            'sunday_month_salary_percentage': 'Hệ số lương tháng ngày chủ nhật',
            'holiday_month_salary_percentage': 'Hệ số lương tháng ngày lễ',
            'normal_hourly_salary': 'Lương theo giờ ngày thường',
            'normal_overtime_hourly_salary': 'Lương theo giờ tăng ca ngày thường',
            'sunday_hourly_salary': 'Lương theo giờ chủ nhật',
            'sunday_overtime_hourly_salary': 'Lương theo giờ tăng ca chủ nhật',
            'holiday_hourly_salary': 'Lương theo giờ ngày lễ',
            'holiday_overtime_hourly_salary': 'Lương theo giờ tăng ca ngày lễ',
            'trip_salary': 'Lương theo chuyến',
            'fixed_allowance': 'Phụ cấp cố định',
            'insurance_amount': 'Số tiền tham gia BHXH',
            'valid_from': 'Hiệu lực từ',
            'note': 'Ghi chú',
        }

        widgets = {
            'driver': forms.Select(attrs={'class': 'form-input', 'required': 'required'}),
            'calculation_method': forms.Select(attrs={'class': 'form-input'}),
            'basic_month_salary': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Nhập lương cơ bản'}),
            'sunday_month_salary_percentage': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Nhập hệ số ngày chủ nhật'}),
            'holiday_month_salary_percentage': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Nhập hệ số ngày lễ'}),
            'normal_hourly_salary': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Nhập lương giờ ngày thường'}),
            'normal_overtime_hourly_salary': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Nhập hệ số tăng ca ngày thường'}),
            'sunday_hourly_salary': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Nhập lương giờ chủ nhật'}),
            'sunday_overtime_hourly_salary': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Nhập hệ số tăng ca chủ nhật'}),
            'holiday_hourly_salary': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Nhập lương giờ ngày lễ'}),
            'holiday_overtime_hourly_salary': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Nhập hệ số tăng ca ngày lễ'}),
            'trip_salary': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Nhập lương theo chuyến'}),
            'fixed_allowance': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Nhập phụ cấp cố định'}),
            'insurance_amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Nhập số tiền BHXH'}),
            'valid_from': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'note': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nhập ghi chú'}),
        }







class DumbTruckPayRateForm(forms.ModelForm):
    class Meta:
        model = DumbTruckPayRate
        fields = [
            'xe', 'chay_ngay', 'chay_dem', 'tanbo_ngay', 'tanbo_dem', 'chay_xa',
            'keo_xe', 'keo_xe_ngay_le', 'chay_ngay_le', 'tanbo_ngay_le', 'chay_xa_dem',
            'luong_co_ban', 'tanbo_cat_bc', 'tanbo_hh', 'chay_thue_sr', 'tanbo_cat_bc_dem',
            'tanbo_doi_3', 'chay_nhua', 'chay_nhua_dem', 'keo_xe_dem'
        ]

        labels = {
            'xe': 'Xe',
            'chay_ngay': 'Chạy ngày',
            'chay_dem': 'Chạy đêm',
            'tanbo_ngay': 'Tanbo ngày',
            'tanbo_dem': 'Tanbo đêm',
            'chay_xa': 'Chạy xa',
            'keo_xe': 'Kéo xe',
            'keo_xe_ngay_le': 'Kéo xe ngày lễ',
            'chay_ngay_le': 'Chạy ngày lễ',
            'tanbo_ngay_le': 'Tanbo ngày lễ',
            'chay_xa_dem': 'Chạy xa đêm',
            'luong_co_ban': 'Lương cơ bản',
            'tanbo_cat_bc': 'Tanbo cát BC',
            'tanbo_hh': 'Tanbo HH',
            'chay_thue_sr': 'Chạy thuê SR',
            'tanbo_cat_bc_dem': 'Tanbo cát BC đêm',
            'tanbo_doi_3': 'Tanbo Đội 3',
            'chay_nhua': 'Chạy nhựa',
            'chay_nhua_dem': 'Chạy nhựa đêm',
            'keo_xe_dem': 'Kéo xe đêm'
        }

        widgets = {
            'xe': forms.Select(attrs={
                'class': 'form-input',
                'required': 'required'
            }),
            'chay_ngay': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương chạy ngày',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'chay_dem': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương chạy đêm',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'tanbo_ngay': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương tanbo ngày',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'tanbo_dem': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương tanbo đêm',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'chay_xa': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương chạy xa',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'keo_xe': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương kéo xe',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'keo_xe_ngay_le': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương kéo xe ngày lễ',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'chay_ngay_le': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương chạy ngày lễ',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'tanbo_ngay_le': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương tanbo ngày lễ',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'chay_xa_dem': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương chạy xa đêm',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'luong_co_ban': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương cơ bản',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'tanbo_cat_bc': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương tanbo cát BC',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'tanbo_hh': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương tanbo HH',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'chay_thue_sr': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương chạy thuê SR',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'tanbo_cat_bc_dem': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương tanbo cát BC đêm',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'tanbo_doi_3': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương tanbo Đội 3',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'chay_nhua': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương chạy nhựa',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'chay_nhua_dem': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương chạy nhựa đêm',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'keo_xe_dem': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương kéo xe đêm',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            })
        }


class DumbTruckRevenueDataForm(forms.ModelForm):
    class Meta:
        model = DumbTruckRevenueData
        fields = ['loai_chay', 'cach_tinh', 'loai_vat_tu', 'moc', 'kich_co_xe', 'don_gia']
        labels = {
            'loai_chay': 'Loại chạy',
            'cach_tinh': 'Cách tính',
            'loai_vat_tu': 'Loại vật tư',
            'moc': 'Mốc',
            'kich_co_xe': 'Kích cỡ xe',
            'don_gia': 'Đơn giá'
        }
        widgets = {
            'loai_chay': forms.Select(attrs={
                'class': 'form-input',
                'required': 'required'
            }),
            'cach_tinh': forms.Select(attrs={
                'class': 'form-input',
                'required': 'required'
            }),
            'loai_vat_tu': forms.Select(attrs={
                'class': 'form-input',
                'required': 'required'
            }),
            'moc': forms.Select(attrs={
                'class': 'form-input',
                'required': 'required'
            }),
            'kich_co_xe': forms.Select(attrs={
                'class': 'form-input',
                'required': 'required'
            }),
            'don_gia': forms.NumberInput(attrs={
                'placeholder': 'Nhập đơn giá',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            })
        }

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'address', 'type_of_location']
        labels = {
            'name': 'Tên địa điểm',
            'address': 'Địa chỉ',
            'type_of_location': 'Loại hình'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Nhập tên địa điểm',
                'class': 'form-input',
                'required': 'required'
            }),
            'address': forms.TextInput(attrs={
                'placeholder': 'Nhập địa chỉ',
                'class': 'form-input',
                'required': 'required'
            }),
            'type_of_location': forms.Select(attrs={
                'class': 'form-input',
                'required': 'required'
            })
        }

class NormalWorkingTimeForm(forms.ModelForm):
    class Meta:
        model = NormalWorkingTime
        fields = ['morning_start', 'morning_end', 'afternoon_start', 'afternoon_end', 'valid_from', 'note']
        labels = {
            'morning_start': 'Bắt đầu ca sáng',
            'morning_end': 'Kết thúc ca sáng',
            'afternoon_start': 'Bắt đầu ca chiều',
            'afternoon_end': 'Kết thúc ca chiều',
            'valid_from': 'Ngày bắt đầu áp dụng',
            'note': 'Ghi chú',
        }
        widgets = {
            'morning_start': forms.TimeInput(attrs={
                'placeholder': 'Chọn giờ bắt đầu ca sáng',
                'class': 'form-input',
                'required': 'required',
                'type': 'time'
            }),
            'morning_end': forms.TimeInput(attrs={
                'placeholder': 'Chọn giờ kết thúc ca sáng',
                'class': 'form-input',
                'required': 'required',
                'type': 'time'
            }),
            'afternoon_start': forms.TimeInput(attrs={
                'placeholder': 'Chọn giờ bắt đầu ca chiều',
                'class': 'form-input',
                'required': 'required',
                'type': 'time'
            }),
            'afternoon_end': forms.TimeInput(attrs={
                'placeholder': 'Chọn giờ kết thúc ca chiều',
                'class': 'form-input',
                'required': 'required',
                'type': 'time'
            }),
            'valid_from': forms.DateInput(attrs={
                'placeholder': 'Chọn ngày bắt đầu áp dụng',
                'class': 'form-input',
                'required': 'required',
                'type': 'date'
            }),
            'note': forms.Textarea(attrs={
                    'class': 'form-input h-20', 
                    'rows': 2
            })
        }

class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['date', 'note']
        labels = {
            'date': 'Ngày lễ',
            'note': 'Ghi chú'
        }
        widgets = {
            'date': forms.DateInput(attrs={
                'placeholder': 'Chọn ngày lễ',
                'class': 'form-input',
                'required': 'required',
                'type': 'date'
            }),
            'note': forms.Textarea(attrs={
                    'class': 'form-input h-20', 
                    'rows': 2
            })

        }


class FuelFillingRecordForm(forms.ModelForm):
    class Meta:
        model = FuelFillingRecord
        fields = ['vehicle', 'litter', 'unit_price','fill_date', 'note']
        labels = {
            'vehicle': 'Xe',
            'litter': 'Số lít',
            'unit_price': 'Đơn giá',
            'fill_date': 'Ngày đổ nhiên liệu',
            'note': 'Ghi chú'
        }
        widgets = {
            'vehicle': forms.Select(attrs={
                'placeholder': 'Chọn xe',
                'class': 'form-input',
                'required': 'required',
            }),
            'litter': forms.NumberInput(attrs={
                'placeholder': 'Số lít',
                'class': 'form-input',
                'required': 'required',
            }),
            'unit_price': forms.NumberInput(attrs={
                'placeholder': 'Đơn giá',
                'class': 'form-input',
                'required': 'required',
            }),

            'fill_date': forms.DateInput(attrs={
                'placeholder': 'Ngày đổ nhiên liệu',
                'class': 'form-input',
                'required': 'required',
                'type': 'date'
            }),
            'note': forms.Textarea(attrs={
                    'class': 'form-input h-20', 
                    'rows': 2
            })
        }

class LubeFillingRecordForm(forms.ModelForm):
    class Meta:
        model = LubeFillingRecord
        fields = ['vehicle', 'litter', 'unit_price', 'fill_date', 'note']
        labels = {
            'vehicle': 'Xe',
            'litter': 'Số lít',
            'unit_price': 'Đơn giá',
            'fill_date': 'Ngày đổ nhớt',
            'note': 'Ghi chú'
        }
        widgets = {
            'vehicle': forms.Select(attrs={
                'placeholder': 'Chọn xe',
                'class': 'form-input',
                'required': 'required',
            }),
            'litter': forms.NumberInput(attrs={
                'placeholder': 'Số lít',
                'class': 'form-input',
                'required': 'required',
            }),
            'unit_price': forms.NumberInput(attrs={
                'placeholder': 'Đơn giá',
                'class': 'form-input',
                'required': 'required',
            }),
            'fill_date': forms.DateInput(attrs={
                'placeholder': 'Chọn ngày đổ nhớt',
                'class': 'form-input',
                'required': 'required',
                'type': 'date'
            }),
            'note': forms.Textarea(attrs={
                    'class': 'form-input h-20', 
                    'rows': 2
            })
        }


class VehicleDepreciationForm(forms.ModelForm):
    class Meta:
        model = VehicleDepreciation
        fields = ['vehicle', 'depreciation_amount', 'from_date', 'to_date', 'note']
        labels = {
            'vehicle': 'Xe',
            'depreciation_amount': 'Khấu hao theo ngày',
            'from_date': 'Ngày bắt đầu',
            'to_date': 'Ngày kết thúc',
            'note': 'Ghi chú'
        }
        widgets = {
            'vehicle': forms.Select(attrs={
                'placeholder': 'Chọn xe',
                'class': 'form-input',
                'required': 'required',
            }),
            'depreciation_amount': forms.NumberInput(attrs={
                'placeholder': 'Khấu hao theo ngày',
                'class': 'form-input',
                'required': 'required',
            }),
            'from_date': forms.DateInput(attrs={
                'placeholder': 'Ngày bắt đầu',
                'class': 'form-input',
                'required': 'required',
                'type': 'date'
            }),
            'to_date': forms.DateInput(attrs={
                'placeholder': 'Ngày kết thúc',
                'class': 'form-input',
                'required': 'required',
                'type': 'date'
            }),
            'note': forms.Textarea(attrs={
                    'class': 'form-input h-20', 
                    'rows': 2
            })
        }

class VehicleBankInterestForm(forms.ModelForm):
    class Meta:
        model = VehicleBankInterest
        fields = ['vehicle', 'interest_amount', 'from_date', 'to_date', 'note']
        labels = {
            'vehicle': 'Xe',
            'interest_amount': 'Lãi suất theo ngày',
            'from_date': 'Ngày bắt đầu',
            'to_date': 'Ngày kết thúc',
            'note': 'Ghi chú'
        }
        widgets = {
            'vehicle': forms.Select(attrs={
                'placeholder': 'Chọn xe',
                'class': 'form-input',
                'required': 'required',
            }),
            'interest_amount': forms.NumberInput(attrs={
                'placeholder': 'Lãi suất theo ngày',
                'class': 'form-input',
                'required': 'required',
            }),
            'from_date': forms.DateInput(attrs={
                'placeholder': 'Ngày bắt đầu',
                'class': 'form-input',
                'required': 'required',
                'type': 'date'
            }),
            'to_date': forms.DateInput(attrs={
                'placeholder': 'Ngày kết thúc',
                'class': 'form-input',
                'required': 'required',
                'type': 'date'
            }),
            'note': forms.Textarea(attrs={
                    'class': 'form-input h-20', 
                    'rows': 2
            })
        }


class VehicleMaintenanceForm(forms.ModelForm):
    class Meta:
        model = VehicleMaintenance
        fields = ['vehicle', 'maintenance_amount', 'maintenance_category', 'from_date', 'to_date', 'approval_status', 'note']
        labels = {
            'vehicle': 'Xe',
            'maintenance_amount': 'Chi phí',
            'maintenance_category': 'Phân loại',
            'from_date': 'Ngày nhận sửa chữa',
            'to_date': 'Ngày xong sửa chữa',
            'approval_status': 'Duyệt',
            'note': 'Ghi chú'
        }
        widgets = {
            'vehicle': forms.Select(attrs={
                'placeholder': 'Chọn xe',
                'class': 'form-input',
                'required': 'required',
                'disabled': 'disabled',
            }),
            'maintenance_amount': forms.NumberInput(attrs={
                'placeholder': 'Chi phí',
                'class': 'form-input',
                'required': 'required',
                'disabled': 'disabled',
            }),
            'maintenance_category': forms.Select(attrs={
                'placeholder': 'Chọn phân loại',
                'class': 'form-input',
                'disabled': 'disabled',
            }, choices=VehicleMaintenance.MAINTENANCE_CATEGORY_CHOICES),
            'from_date': forms.DateInput(attrs={
                'placeholder': 'Ngày nhận sửa chữa',
                'class': 'form-input',
                'required': 'required',
                'type': 'date',
                'disabled': 'disabled'
            }),
            'to_date': forms.DateInput(attrs={
                'placeholder': 'Ngày xong sửa chữa',
                'class': 'form-input',
                'required': 'required',
                'type': 'date',
                'disabled': 'disabled'
            }),
            'approval_status': forms.Select(attrs={
                'placeholder': 'Chọn trang thái phê duyệt',
                'class': 'form-input',
                'disabled': 'disabled',
            }, choices=VehicleMaintenance.APPROVAL_STATUS_CHOICES),
            'note': forms.Textarea(attrs={
                    'class': 'form-input h-20',
                    'disabled': 'disabled',
                    'rows': 2
            })
        }


class RepairPartForm(forms.ModelForm):
    class Meta:
        model = RepairPart
        fields = ['vehicle_type', 'part_number', 'part_name', 'part_price', 'image', 'valid_from', 'note']
        labels = {
            'vehicle_type': 'Loại xe',
            'part_number': 'Mã phụ tùng',
            'part_name': 'Tên đầy đủ',
            'part_price': 'Đơn giá',
            'image': 'Hình ảnh',
            'valid_from': 'Ngày áp dụng',
            'note': 'Ghi chú'
        }
        widgets = {
            'vehicle_type': forms.Select(attrs={
                'placeholder': 'Chọn loại xe',
                'class': 'form-input',
                'required': 'required',
            }),

            'part_number': forms.TextInput(attrs={
                'placeholder': 'Mã bộ phận',
                'class': 'form-input',
                'required': 'required',
            }),
            'part_name': forms.TextInput(attrs={
                'placeholder': 'Tên phần',
                'class': 'form-input',
                'required': 'required',
            }),
            'part_price': forms.NumberInput(attrs={
                'placeholder': 'Đơn giá',
                'class': 'form-input',
                'required': 'required',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-input-file',
            }),
            'valid_from': forms.DateInput(attrs={
                'placeholder': 'Ngày áp dụng',
                'class': 'form-input',
                'required': 'required',
                'type': 'date'
            }),
            'note': forms.Textarea(attrs={
                    'class': 'form-input h-20', 
            }),
        }


class UserPermissionForm(forms.ModelForm):
    class Meta:
        model = UserPermission
        fields = ['user', 'permission', 'note']
        labels = {
            'user': 'Tài khoản',
            'permission': 'Quyền',
            'note': 'Ghi chú',
        }
        widgets = {
            'user': forms.Select(attrs={
                'placeholder': 'Chọn tài khoản',
                'class': 'form-input',
                'required': 'required',
            }),
            'permission': forms.Select(attrs={
                'placeholder': 'Chọn quyền',
                'class': 'form-input',
                'required': 'required',
            }, choices=UserPermission.PERMISSION_CHOICES),
            'note': forms.Textarea(attrs={
                    'class': 'form-input h-20', 
            }),
        }


class ProjectUserForm(forms.ModelForm):
    class Meta:
        model = ProjectUser
        fields = ['user', 'project', 'role', 'note']
        labels = {
            'user': 'Tài khoản',
            'project': 'Dự án',
            'role': 'Vị trí',
            'note': 'Ghi chú',
        }
        widgets = {
            'user': forms.Select(attrs={
                'placeholder': 'Chọn tài khoản',
                'class': 'form-input',
                'required': 'required',
            }),
            'project': forms.Select(attrs={
                'placeholder': 'Chọn dự án',
                'class': 'form-input',
                'required': 'required',
            }),
            'role': forms.Select(attrs={
                'placeholder': 'Chọn vị trí',
                'class': 'form-input',
                'required': 'required',
            }, choices=ProjectUser.ROLE_CHOICES),
            'note': forms.Textarea(attrs={
                    'class': 'form-input h-20', 
            }),
        }
