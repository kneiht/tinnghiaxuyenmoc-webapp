
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
        fields = ['name', 'status', 'description', 'start_date', 'end_date', 'image']

    
        labels = {
            'name': 'Tên dự án',
            'status': 'Trạng thái',
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
            'status': forms.Select(attrs={
                    'class': 'form-input'}),
            'description': forms.Textarea(attrs={
                    'class': 'form-input', 
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
            'category': 'Loại công việc',
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
                    'class': 'form-input', 
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

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        project = cleaned_data.get('project')
        # Validate date
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError('Ngày bắt đầu phải nhỏ hoặc bằng ngày kết thúc.')
            
        # Check if job end date is after project end date
        if end_date > project.end_date:
                raise ValidationError(f'Ngày kết thúc phải nhỏ hoặc bằng ngày kết thúc dự án {project.end_date.strftime("%d/%m/%Y")}.')
    
        return cleaned_data


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






class DataVehicleForm(forms.ModelForm):
    class Meta:
        model = DataVehicle
        fields = ['vehicle_type', 'license_plate', 'vehicle_name', 'gps_name', 'vehicle_inspection_number', 'vehicle_inspection_due_date']

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



from .models import DataDriver
class DataDriverForm(forms.ModelForm):
    class Meta:
        model = DataDriver
        fields = [
            'full_name', 'status', 'hire_date', 'identity_card', 'birth_year',
            'basic_salary', 'hourly_salary', 'trip_salary', 'bank_name', 'account_number',
            'account_holder_name', 'fixed_allowance', 'insurance_amount',
            'phone_number', 'address'
        ]
        
        labels = {
            'full_name': 'Họ và tên',
            'status': 'Trang thái',
            'hire_date': 'Ngày vào làm',
            'identity_card': 'CCCD',
            'birth_year': 'Ngày sinh',
            'basic_salary': 'Lương cơ bản',
            'hourly_salary': 'Lương theo giờ',
            'bank_name': 'Ngân hàng',
            'account_number': 'Số tài khoản',
            'account_holder_name': 'Tên chủ tài khoản',
            'fixed_allowance': 'Phụ cấp cố định',
            'insurance_amount': 'Số tiền tham gia BHXH',
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
                'class': 'form-input',  # Add select input for status
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
            'basic_salary': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương cơ bản',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'hourly_salary': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương theo giờ',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),

            'trip_salary': forms.NumberInput(attrs={
                'placeholder': 'Nhập lương theo chuyến',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),



            'bank_name': forms.TextInput(attrs={
                'placeholder': 'Nhập tên ngân hàng',
                'class': 'form-input',
                'required': 'required'
            }),
            'account_number': forms.TextInput(attrs={
                'placeholder': 'Nhập số tài khoản',
                'class': 'form-input',
                'required': 'required'
            }),
            'account_holder_name': forms.TextInput(attrs={
                'placeholder': 'Nhập tên chủ tài khoản',
                'class': 'form-input',
                'required': 'required'
            }),
            'fixed_allowance': forms.NumberInput(attrs={
                'placeholder': 'Nhập phụ cấp cố định',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'insurance_amount': forms.NumberInput(attrs={
                'placeholder': 'Nhập số tiền tham gia BHXH',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
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


from .models import DataVehicleTypeDetail
class DataVehicleTypeDetailForm(forms.ModelForm):
    class Meta:
        model = DataVehicleTypeDetail
        fields = [
            'vehicle_type', 'vehicle_type_detail', 'revenue_per_8_hours', 
            'oil_consumption_per_hour', 'lubricant_consumption', 'insurance_fee', 
            'road_fee_inspection', 'tire_wear', 'police_fee'
        ]

        labels = {
            'vehicle_type': 'Loại xe',
            'vehicle_type_detail': 'Loại xe chi tiết',
            'revenue_per_8_hours': 'Đơn giá doanh thu/8 tiếng',
            'oil_consumption_per_hour': 'Định mức dầu 1 tiếng',
            'lubricant_consumption': 'Định mức nhớt',
            'insurance_fee': 'Định mức bảo hiểm',
            'road_fee_inspection': 'Định mức sử dụng đường bộ/Đăng kiểm',
            'tire_wear': 'Định mức hao mòn lốp xe',
            'police_fee': 'Định mức CA'
        }

        widgets = {
            'vehicle_type': forms.Select(attrs={
                'class': 'form-input',
                'required': 'required'
            }),
            'vehicle_type_detail': forms.TextInput(attrs={
                'placeholder': 'Nhập loại xe chi tiết',
                'class': 'form-input',
                'required': 'required'
            }),
            'revenue_per_8_hours': forms.NumberInput(attrs={
                'placeholder': 'Nhập đơn giá doanh thu/8 tiếng',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'oil_consumption_per_hour': forms.NumberInput(attrs={
                'placeholder': 'Nhập định mức dầu 1 tiếng',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'lubricant_consumption': forms.NumberInput(attrs={
                'placeholder': 'Nhập định mức nhớt',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'insurance_fee': forms.NumberInput(attrs={
                'placeholder': 'Nhập định mức bảo hiểm',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'road_fee_inspection': forms.NumberInput(attrs={
                'placeholder': 'Nhập định mức sử dụng đường bộ/Đăng kiểm',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'tire_wear': forms.NumberInput(attrs={
                'placeholder': 'Nhập định mức hao mòn lốp xe',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            }),
            'police_fee': forms.NumberInput(attrs={
                'placeholder': 'Nhập định mức CA',
                'class': 'form-input',
                'step': '0.01',
                'required': 'required'
            })
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
