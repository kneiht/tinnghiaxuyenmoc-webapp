
from django import forms
from datetime import datetime
from django.shortcuts import get_object_or_404


from django.db.models import Exists, OuterRef

from .models import (Project, Job, ProjectUser, User, DataVehicle)



class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'status', 'description', 'image', 'start_date', 'end_date']

    
        labels = {
            'name': 'Tên dự án',
            'status': 'Trạng thái',
            'description': 'Mô tả',
            'image': 'Hình ảnh',
            'start_date': 'Thời điểm bắt đầu',
            'end_date': 'Thời điểm kết thúc',
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




class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['project', 'name', 'status', 'category', 'unit', 'quantity', 'description', 'start_date', 'end_date']

        labels = {
            'status': 'Trạng thái',
            'name': 'Tên công việc',
            'category': 'Loại công việc',
            'unit': 'Đơn vị',
            'quantity': 'Số lượng',
            'description': 'Mô tả',
            'start_date': 'Thời điểm bắt đầu',
            'end_date': 'Thời điểm kết thúc',
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
                    'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={
                    'placeholder': 'Số lượng',
                    'class': 'form-input'}),
            'description': forms.Textarea(attrs={
                    'class': 'form-input', 
                    'rows': 2}),
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






# from django import forms
# from datetime import datetime
# from django.shortcuts import get_object_or_404


# from django.db.models import Exists, OuterRef

# from .models import (School, Student, Class, 
#                      StudentClass, FinancialTransaction, Attendance)

# class SchoolForm(forms.ModelForm):
#     class Meta:
#         model = School
#         fields = ['name', 'description', 'image', 'zalo']
#         help_texts = {
#             'abbreviation': 'This is used as a prefix to student ID',
#         }
    
#         widgets = {
#             'name': forms.TextInput(attrs={
#                     'placeholder': 'Your school name',
#                     'required': 'required',
#                     'class': 'form-input'}),
#             'abbreviation': forms.TextInput(attrs={
#                     'placeholder': 'Your school abbreviation',
#                     'class': 'form-input'}),
#             'description': forms.Textarea(attrs={
#                     'class': 'form-input', 
#                     'rows': 2}),
#             'image': forms.FileInput(attrs={
#                     'class': 'form-input-file',}),

#             'zalo': forms.TextInput(attrs={
#                     'placeholder': 'Zalo link',
#                     'required': 'required',
#                     'class': 'form-input'}),

#         }


# class StudentForm(forms.ModelForm):
#     class Meta:
#         model = Student
#         fields = ['name', 'status', 'gender', 'date_of_birth', 'mother', 'mother_phone', 'father', 'father_phone', 'reward_points', 'note', 'image', 'image_portrait', 'classes']
        
#         help_texts = {
#             'image': 'Upload an image the student likes',
#             'image_portrait': 'Upload an student portrait. (Hình chân dung)',
#         }
        
#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'placeholder': 'Student name',
#                 'required': 'required',
#                 'class': 'form-input'
#             }),
#             'gender': forms.Select(attrs={
#                 'class': 'form-input'
#             }),
#             'date_of_birth': forms.DateInput(attrs={
#                 'class': 'form-input',
#                 'type': 'date'
#             }),
#             'mother': forms.TextInput(attrs={
#                 'placeholder': "Student's mother",
#                 'class': 'form-input'
#             }),
#             'mother_phone': forms.TextInput(attrs={
#                 'placeholder': 'Mother\'s phone number',
#                 'class': 'form-input'
#             }),

#             'father': forms.TextInput(attrs={
#                 'placeholder': "Student's father",
#                 'class': 'form-input'
#             }),
#             'father_phone': forms.TextInput(attrs={
#                 'placeholder': 'Father\'s phone number',
#                 'class': 'form-input'
#             }),


#             'status': forms.Select(attrs={
#                 'class': 'form-input'
#             }),
#             'note': forms.Textarea(attrs={
#                 'class': 'form-input',
#                 'rows': 2
#             }),
#             'reward_points': forms.NumberInput(attrs={
#                 'class': 'form-input'
#             }),
#             'image': forms.FileInput(attrs={
#                 'class': 'form-input-file',
#             }),
#             'image_portrait': forms.FileInput(attrs={
#                 'class': 'form-input-file'
#             }),
#         }
#     def __init__(self, *args, **kwargs):
#         school_id = kwargs.pop('school_id', None)
#         super().__init__(*args, **kwargs)
#         if school_id is not None:
#             self.school_id = school_id
#         else:
#             self.school_id = None

#         # Set the choices of the status field
#         if self.instance.is_converted_to_student:
#             self.fields['status'].choices = Student.STUDENT_STATUS
#         else:
#             self.fields['status'].choices = Student.CRM_STATUS


#     def get_classes(self):
#         student_instance = self.instance
#         #print(student_instance)
#         # Check if the student instance exists
#         if not student_instance.pk:
#             # The student isn't saved yet; return all classes from the specified school without extra processing
#             return Class.objects.filter(school_id=self.school_id).order_by('-pk')

#         # Annotate each class with a flag indicating if the student is in this class
#         student_in_class_subquery = StudentClass.objects.filter(
#             student=student_instance, _class=OuterRef('pk')
#         )
#         classes = Class.objects.filter(school_id=self.school_id).annotate(
#             in_class=Exists(student_in_class_subquery)
#         ).order_by('-in_class', '-pk')
#         #print(classes)
#         # Convert the QuerySet to a list to avoid duplicate queries on iteration
#         classes_list = list(classes)

#         # Fetch all StudentClass instances for the current student to reduce query count
#         student_classes = {sc._class_id: sc for sc in StudentClass.objects.filter(student=student_instance)}

#         # Set `is_payment_required` on each class object
#         for _class in classes_list:
#             # Check if there's a StudentClass instance for this student and class
#             student_class = student_classes.get(_class.id)
#             if student_class:
#                 # Directly attach the is_payment_required attribute from StudentClass
#                 _class.is_payment_required = student_class.is_payment_required
#             else:
#                 # Default to False if no StudentClass instance exists
#                 _class.is_payment_required = False

#         return classes_list



# class StudentNoteForm(forms.ModelForm):
#     class Meta:
#         model = Student
#         fields = ['last_note']
#         labels = {
#             'last_note': 'Your quick note'
#         }
#         help_texts = {
#             'last_note': 'Date and time will be added automatically'
#         }
#         widgets = {
#             'last_note': forms.Textarea(attrs={
#                 'class': 'form-input',
#                 'rows': 2
#             }),
#         }

#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         new_note = self.cleaned_data['last_note']
#         current_date = datetime.now().strftime("- %d-%m-%Y %H:%M")
#         if instance.note:
#             instance.note = f'{current_date}: {new_note}\n' +  instance.note # Append the new note to the current note
#             #print(instance.note)
#         else:
#             instance.note = f'{current_date}: {new_note}'  # If there's no current note, set the new note
#         instance.last_note = ""
#         if commit:
#             instance.save()
#             #print(instance.last_note)
#         return instance

# class StudentConvertForm(forms.ModelForm):
#     class Meta:
#         model = Student
        
#         fields = ['is_converted_to_student']
#         labels = {
#             'is_converted_to_student': 'Do you want to convert this customer into a student?'
#         }
#         help_texts = {
#             'is_converted_to_student': 'Be careful! Only convert a customer who already paid tuition. When you convert a customer into a student, it can not be converted back to the CRM. The status of the student will be set to "Enrolled" by default.'
#         }
#         widgets = {
#             'is_converted_to_student': forms.CheckboxInput(attrs={
#                 'class': 'checkbox'
#             }),
#         }





# class ClassForm(forms.ModelForm):
#     class Meta:
#         model = Class
#         fields = ['name', 'status', 'price_per_hour', 'time_frame', 'image',  'zalo', 'note', 'students', ]
#         widgets = {
#             'name': forms.TextInput(attrs={
#                 'placeholder': 'Class name',
#                 'required': 'required',
#                 'class': 'form-input'
#             }),
#             'status': forms.Select(attrs={
#                 'class': 'form-input'
#             }),

#             'time_frame': forms.Select(attrs={
#                 'placeholder': 'Schedule',
#                 'required': 'required',
#                 'class': 'form-input'
#             }),

#             'image': forms.FileInput(attrs={
#                 'class': 'form-input-file'
#             }),
#             'price_per_hour': forms.NumberInput(attrs={
#                 'class': 'form-input'
#             }),
#             'zalo': forms.TextInput(attrs={
#                 'placeholder': 'Zalo link',
#                 'required': 'required',
#                 'class': 'form-input'
#             }),
#             'note': forms.Textarea(attrs={
#                 'class': 'form-input',
#                 'rows': 2
#             }),
#         }

#     def __init__(self, *args, **kwargs):
#         school_id = kwargs.pop('school_id', None)
#         super().__init__(*args, **kwargs)
#         if school_id is not None:
#             self.school_id = school_id
#         else:
#             self.school_id = None

#     def get_students(self):
#         class_instance = self.instance

#         # Check if the class instance exists
#         if not class_instance.pk:
#             # The class isn't saved yet; return all students from the specified school without extra processing
#             return Student.objects.filter(school_id=self.school_id).order_by('-pk')

#         # Annotate each student with a flag indicating if they are in this class
#         student_in_class_subquery = StudentClass.objects.filter(
#             student=OuterRef('pk'), _class=class_instance
#         )
#         students = Student.objects.filter(school_id=self.school_id).annotate(
#             in_class=Exists(student_in_class_subquery)
#         ).order_by('-in_class', '-pk')

#         # Convert the QuerySet to a list to avoid duplicate queries on iteration
#         students_list = list(students)

#         # Fetch all StudentClass instances for the current class to reduce query count
#         student_classes = {sc.student_id: sc for sc in StudentClass.objects.filter(_class=class_instance)}

#         # Set `is_payment_required` on each student object
#         for student in students_list:
#             # Check if there's a StudentClass instance for this student and class
#             student_class = student_classes.get(student.id)
#             if student_class:
#                 # Directly attach the is_payment_required attribute from StudentClass
#                 student.is_payment_required = student_class.is_payment_required
#             else:
#                 # Default to False if no StudentClass instance exists
#                 student.is_payment_required = False

#         return students_list



# class AttendanceForm(forms.ModelForm):
#     # form for attendance
#     class Meta:
#         model = Attendance
#         fields = ['check_date', 'student', 'check_class', 'status', 'is_payment_required', 'use_price_per_hour_from_class', 'price_per_hour', 'learning_hours', 'note', ]
#         widgets = {
#             'check_date': forms.DateInput(attrs={
#                 'class': 'form-input',
#                 'type': 'date'
#             }),

#             'student': forms.Select(attrs={
#                 'class': 'form-input'
#             }),

#             'check_class': forms.Select(attrs={
#                 'class': 'form-input'
#             }),
#             'use_price_per_hour_from_class': forms.CheckboxInput(attrs={
#                 'class': 'checkbox'
#             }),
#             'is_payment_required': forms.CheckboxInput(attrs={
#                 'class': 'checkbox'
#             }),

#             'status': forms.Select(attrs={
#                 'class': 'form-input'
#             }),
#             'learning_hours': forms.NumberInput(attrs={
#                 'class': 'form-input'
#             }),
#             'note': forms.Textarea(attrs={
#                 'class': 'form-input',
#                 'rows': 2
#             }),
#             'price_per_hour': forms.NumberInput(attrs={
#                 'class': 'form-input'
#             }),
#         }
#     def __init__(self, *args, **kwargs):
#         school_id = kwargs.pop('school_id', None)
#         super().__init__(*args, **kwargs)
#         self.school_id = school_id
#         # Set the choices of the status field
#         self.fields['check_class'].choices = Class.objects.filter(school_id=self.school_id).values_list('id', 'name')



# class FinancialTransactionForm(forms.ModelForm):
#     class Meta:
#         model = FinancialTransaction
#         fields = ['income_or_expense', 'transaction_type', 
#                   'giver', 'receiver', 'amount', 'student', 
#                   'bonus', 'student_balance_increase', 'created_at','note',
#                   'image1', 'image2', 'image3', 'image4']
#         widgets = {
#             'income_or_expense': forms.Select(attrs={
#                 'class': 'form-input'
#             }),
#             'transaction_type': forms.Select(attrs={
#                 'class': 'form-input'
#             }),
#             'giver': forms.TextInput(attrs={
#                 'class': 'form-input'
#             }),
#             'receiver': forms.TextInput(attrs={
#                 'class': 'form-input'
#             }),
#             'amount': forms.NumberInput(attrs={
#                 'class': 'form-input'
#             }),
#             'created_at': forms.DateInput(attrs={
#                 'class': 'form-input',
#                 'type': 'date'
#             }),
#             'note': forms.Textarea(attrs={
#                 'class': 'form-input',
#                 'rows': 2
#             }),

#             'student': forms.Select(attrs={
#                 'class': 'form-input',
#             }),

#             'bonus': forms.Select(attrs={
#                 'class': 'form-input',
#             }),

#             'student_balance_increase': forms.NumberInput(attrs={
#                 'class': 'form-input',
#             }),

#             'image1': forms.FileInput(attrs={
#                     'class': 'form-input-file',}),
#             'image2': forms.FileInput(attrs={
#                     'class': 'form-input-file',}),
#             'image3': forms.FileInput(attrs={
#                     'class': 'form-input-file',}),
#             'image4': forms.FileInput(attrs={
#                     'class': 'form-input-file',}),
#             'image5 ': forms.FileInput(attrs={
#                     'class': 'form-input-file',}),
#         }

# class TuitionPaymentForm(forms.ModelForm):
#     class Meta:
#         model = FinancialTransaction
#         fields = ['income_or_expense', 'transaction_type', 'student', 'receiver', 'amount', 'bonus', 'note']
#         widgets = {
#             'income_or_expense': forms.Select(attrs={
#                 'class': 'form-input disabled',
#             }),
#             'transaction_type': forms.Select(attrs={
#                 'class': 'form-input',
#             }),
#             'student': forms.Select(attrs={
#                 'class': 'form-input',
#             }),
#             'receiver': forms.TextInput(attrs={
#                 'class': 'form-input',
#             }),
#             'amount': forms.NumberInput(attrs={
#                 'class': 'form-input'
#             }),
#             'bonus': forms.Select(attrs={
#                 'class': 'form-input',
#             }),

#             'student_balance_increase': forms.NumberInput(attrs={
#                 'class': 'form-input',
#             }),
#             'created_at': forms.DateInput(attrs={
#                 'class': 'form-input',
#                 'type': 'date'
#             }),

#             'note': forms.Textarea(attrs={
#                 'class': 'form-input',
#                 'rows': 2
#             }),
#         }

#     def __init__(self, *args, **kwargs):
#         school_id = kwargs.pop('school_id', None)
#         student_id = kwargs.pop('student_id', None)
#         super().__init__(*args, **kwargs)
#         if school_id is not None:
#             self.school_id = school_id
#             self.student_id = student_id
#         else:
#             self.school_id = None
#             self.student_id = None

#     def get_payments(self):
#         payments = FinancialTransaction.objects.filter(school_id=self.school_id,student_id=self.student_id).order_by('created_at')
#         return payments



# class TuitionPaymentOldForm(forms.ModelForm):
#     class Meta:
#         model = FinancialTransaction
#         fields = ['income_or_expense', 'transaction_type', 'student', 'receiver', 'amount', 'note', 'student_balance_increase']
#         widgets = {
#             'income_or_expense': forms.Select(attrs={
#                 'class': 'form-input disabled',
#             }),
#             'transaction_type': forms.Select(attrs={
#                 'class': 'form-input',
#             }),
#             'student': forms.Select(attrs={
#                 'class': 'form-input',
#             }),
#             'receiver': forms.TextInput(attrs={
#                 'class': 'form-input',
#             }),
#             'amount': forms.Select(
#                 choices = [(0, "Chọn gói học phí"),
#                            (1800000, "Mầm non và tiểu học - Quý 1.800.000 VNĐ (gốc)"),
#                            (1620000, "Mầm non và tiểu học - Quý 1.620.000 VNĐ (gốc - 10%)"),
#                            (1440000, "Mầm non và tiểu học - Quý 1.440.000 VNĐ (gốc - 20%)"),
#                            (1350000, "Mầm non và tiểu học - Quý 1.350.000 VNĐ (gốc - 25%)"),
#                            (1300000, "Mầm non và tiểu học - Quý 1.300.000 VNĐ (Hp chính sách cũ)"),
#                            (3240000, "Mầm non và tiểu học - Nửa năm 3.240.000 VNĐ (gốc)"),
#                            (2916000, "Mầm non và tiểu học - Nửa năm 2.916.000 VNĐ (gốc - 10%)"),
#                            (5640000, "Mầm non và tiểu học - Năm 5.640.000 VNĐ (gốc)"),
#                            (5076000, "Mầm non và tiểu học - Năm 5.076.000 VNĐ (gốc - 10%)"),
                           

#                            (2200000, "Trung học và giao tiếp - Quý 2.200.000 VNĐ (gốc)"),
#                            (1980000, "Trung học và giao tiếp - Quý 1.980.000 VNĐ (gốc - 10%)"),
#                            (3960000, "Trung học và giao tiếp - Nửa năm 3.960.000 VNĐ (gốc)"),
#                            (3564000, "Trung học và giao tiếp - Nửa năm 3.564.000 VNĐ (gốc - 10%)"),
#                            (7080000, "Trung học và giao tiếp - Năm 7.080.000 VNĐ (gốc)"),
#                            (6372000, "Trung học và giao tiếp - Năm 6.372.000 VNĐ (gốc - 10%)"),
#                            ],



#                 attrs={
#                 'class': 'form-input'
#             }),

#             'note': forms.Textarea(attrs={
#                 'class': 'form-input',
#                 'rows': 2
#             }),
#         }

#     def __init__(self, *args, **kwargs):
#         school_id = kwargs.pop('school_id', None)
#         student_id = kwargs.pop('student_id', None)
#         super().__init__(*args, **kwargs)
#         if school_id is not None:
#             self.school_id = school_id
#             self.student_id = student_id
#         else:
#             self.school_id = None
#             self.student_id = None

#     def get_payments(self):
#         payments = FinancialTransaction.objects.filter(school_id=self.school_id,student_id=self.student_id).order_by('created_at')
#         return payments


# class TuitionPaymentSpecialForm(forms.ModelForm):
#     class Meta:
#         model = FinancialTransaction
#         fields = ['income_or_expense', 'transaction_type', 'student', 'receiver', 'amount', 'student_balance_increase', 'note']
#         widgets = {
#             'income_or_expense': forms.Select(attrs={
#                 'class': 'form-input disabled',
#             }),
#             'transaction_type': forms.Select(attrs={
#                 'class': 'form-input',
#             }),
#             'student': forms.Select(attrs={
#                 'class': 'form-input',
#             }),
#             'receiver': forms.TextInput(attrs={
#                 'class': 'form-input',
#             }),
#             'amount': forms.NumberInput(attrs={
#                 'class': 'form-input'
#             }),
#             'student_balance_increase': forms.NumberInput(attrs={
#                 'class': 'form-input'
#             }),
#             'note': forms.Textarea(attrs={
#                 'class': 'form-input',
#                 'rows': 2
#             }),
#         }

#     def __init__(self, *args, **kwargs):
#         school_id = kwargs.pop('school_id', None)
#         student_id = kwargs.pop('student_id', None)
#         super().__init__(*args, **kwargs)
#         if school_id is not None:
#             self.school_id = school_id
#             self.student_id = student_id
#         else:
#             self.school_id = None
#             self.student_id = None

#     def get_payments(self):
#         payments = FinancialTransaction.objects.filter(school_id=self.school_id,student_id=self.student_id).order_by('created_at')
#         return payments


