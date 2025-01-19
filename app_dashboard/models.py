# Standard library imports
import io
import re
import time
from datetime import date, datetime, time, timedelta

# Django imports
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Max, Sum
from django.db.models.fields.files import ImageFieldFile
from django.utils import timezone

# Third-party library imports
import pandas as pd
from PIL import Image

def get_valid_date(date):
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    except:
        date = timezone.now().date()
    date = date.strftime('%Y-%m-%d')
    return date

def get_str_return(self):
    if self.first_name in ('', None):
        name = "Chưa cập nhật tên"
    else:
        name = self.first_name
    return self.username + " (" + name +")"


@classmethod
def get_display_fields(self):
    fields = ['username', 'first_name', 'email', 'is_superuser']
    # Check if the field is in the model
    for field in fields:
        if not hasattr(self, field):
            fields.remove(field)
    return fields


def check_permission(self, sub_page):
    class Permission:
        read = False
        create = False
        update = False
        delete = False
        approve = False

    return_permission = Permission()

    if self.is_superuser:
        return_permission.read = True
        return_permission.create = True
        return_permission.update = True
        return_permission.delete = True
        return_permission.approve = True

    user_permissions = UserPermission.objects.filter(user=self, sub_page=sub_page)
    # get all permission in user_permissions
    if user_permissions:
        for permission in user_permissions:
            if permission.permission:
                for item in  ['read', 'create', 'update', 'delete', 'approve']:
                    if item in permission.permission:
                        setattr(return_permission, item, True)

    return return_permission



User.add_to_class("__str__", get_str_return)
User.add_to_class("get_display_fields", get_display_fields)
User.add_to_class("check_permission", check_permission)




class BaseModel(models.Model):
    last_saved = models.DateTimeField(default=timezone.now, blank=True, null=True)
    archived = models.BooleanField(default=False)

    class Meta:
        abstract = True  # Specify this model as Abstract

    def compress_image(self, image_field, max_width):
        try:
            # Open the uploaded image using PIL
            image_temp = Image.open(image_field)
        except FileNotFoundError:
            return  # Return from the method if the file is not found

        if '_compressed' in image_field.name:
            return image_field

        # Resize the image if it is wider than 600px
        if image_temp.width > max_width:
            # Calculate the height with the same aspect ratio
            height = int((image_temp.height / image_temp.width) * max_width)
            image_temp = image_temp.resize((max_width, height), Image.Resampling.LANCZOS)

        # Define the output stream for the compressed image
        output_io_stream = io.BytesIO()

        # Save the image to the output stream with desired quality
        image_temp.save(output_io_stream, format='WEBP', quality=40)
        output_io_stream.seek(0)

        # Create a Django InMemoryUploadedFile from the compressed image
        file_name = "%s_compressed.webp" % image_field.name.split('.')[0]
        output_imagefield = InMemoryUploadedFile(output_io_stream, 'ImageField', 
                                                 file_name, 
                                                 'image/webp', output_io_stream.getbuffer().nbytes, None)
        
        return output_imagefield

    def create_thumbnail(self, image_field):
        max_width = 60
        try:
            # Open the uploaded image using PIL
            image_temp = Image.open(image_field)
        except FileNotFoundError:
            return  # Return from the method if the file is not found

        height = int((image_temp.height / image_temp.width) * max_width)
        image_temp = image_temp.resize((max_width, height), Image.Resampling.LANCZOS)
        output_io_stream = io.BytesIO()

        # Save the image to the output stream with desired quality
        image_temp.save(output_io_stream, format='WEBP', quality=40)
        output_io_stream.seek(0)

        # Create a Django InMemoryUploadedFile from the compressed image
        file_name = "%s.thumbnail" % image_field.name.split('.')[0]
        output_imagefield = InMemoryUploadedFile(output_io_stream, 'ImageField', 
                                                 file_name, 
                                                 'image/webp', output_io_stream.getbuffer().nbytes, None)

        return output_imagefield

    def save(self, *args, **kwargs):
        # refine fields
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, ImageFieldFile):
                if value:  # If there's an image to compress
                    compressed_image = self.compress_image(value, 500)
                    setattr(self, field.name, compressed_image)

                    if not Thumbnail.objects.filter(reference_url=value.url).exists():
                        thumbnail_image = self.create_thumbnail(value)
                        thumbnail = Thumbnail.objects.create(
                            reference_url=value.url,
                            thumbnail=None
                        )
                        setattr(thumbnail, 'thumbnail', thumbnail_image)
                        thumbnail.save()

            elif isinstance(value, str):
                # Remove leading and trailing whitespaces
                value = value.strip()
                # Replace multiple spaces with a single space
                value = re.sub(r' +', ' ', value)
                setattr(self, field.name, value)

        super().save(*args, **kwargs)

        for field in self._meta.fields:
            value = getattr(self, field.name)
            if isinstance(value, ImageFieldFile):
                if value:  # If there's an image to create thumbnail
                    if not Thumbnail.objects.filter(reference_url=value.url).exists():
                        thumbnail_image = self.create_thumbnail(value)
                        thumbnail = Thumbnail.objects.create(
                            reference_url=value.url,
                            thumbnail=None
                        )
                        setattr(thumbnail, 'thumbnail', thumbnail_image)
                        thumbnail.save()

class Thumbnail(models.Model):
    reference_url = models.CharField(max_length=255, blank=True, null=True)
    thumbnail  = models.ImageField(upload_to='images/thumbnails/', blank=True, null=True)

class SecondaryIDMixin(models.Model):
    secondary_id = models.IntegerField(blank=True, null=True)
    class Meta:
        abstract = True  # This makes it a mixin, not a standalone model

    def save(self, *args, **kwargs):
        if self._state.adding and hasattr(self, 'project'):
            with transaction.atomic():
                highest_id = self.__class__.objects.filter(
                    project=self.project
                ).aggregate(max_secondary_id=Max('secondary_id'))['max_secondary_id'] or 0
                self.secondary_id = highest_id + 1
        super().save(*args, **kwargs)

class UserPermission(BaseModel):
    MODEL_PERMISSION_CHOICES = (
        ('read', 'Đọc'),
        ('read_create', 'Đọc - Tạo'),
        ('read_create_update', 'Đọc - Tạo - Cập nhật'),
        ('read_create_update_delete', 'Đọc - Tạo - Cập nhật - Xóa'),
        ('read_create_update_delete_approve', 'Đọc - Tạo - Cập nhật - Xóa - Duyệt'),
    )

    MODEL_CHOICES = (
        # From the first dictionary
        ('Announcement', 'Thông báo'),
        ('Task', 'Công việc'),
        ('User', 'Tài khoản nhân viên'),
        ('UserPermission', 'Cấp quyền quản lý dữ liệu'),
        ('ProjectUser', 'Cấp quyền quản lý dự án'),

        ('VehicleType', 'DL loại xe'),
        ('VehicleRevenueInputs', 'DL tính DT theo loại xe'),
        ('VehicleDetail', 'DL xe chi tiết'),
        ('StaffData', 'DL nhân viên'),
        ('DriverSalaryInputs', 'DL mức lương tài xế'),
        ('DumbTruckPayRate', 'DL tính lương tài xế xe ben'),
        ('DumbTruckRevenueData', 'DL tính DT xe ben'),
        ('Location', 'DL địa điểm'),
        ('NormalWorkingTime', 'Thời gian làm việc'),
        ('Holiday', 'Ngày lễ'),

        ('LiquidUnitPrice', 'Bảng đơn giá nhiên liệu/nhớt'),
        ('FillingRecord', 'LS đổ nhiên liệu/nhớt'),
        ('FuelFillingRecord', 'LS đổ nhiên liệu'),
        ('LubeFillingRecord', 'LS đổ nhớt'),
        ('PartProvider', 'Nhà cung cấp phụ tùng'),
        ('RepairPart', 'Danh mục sửa chữa'),
        ('PaymentRecord', 'Lịch sử thanh toán'),
        ('VehicleMaintenance', 'Phiếu sửa chữa'),
        ('VehicleDepreciation', 'Khấu hao'),
        ('VehicleBankInterest', 'Lãi ngân hàng'),
        ('VehicleOperationRecord', 'DL HĐ xe công trình / ngày'),
        ('ConstructionDriverSalary', 'Bảng lương'),
        ('ConstructionReportPL', 'Bảng BC P&L xe cơ giới'),
    )

    class Meta:
        ordering = ['user', 'sub_page', 'created_at']
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Tài khoản")
    sub_page = models.CharField(max_length=255, choices=MODEL_CHOICES, verbose_name="Bảng dữ liệu", null=True, blank=True)
    permission = models.CharField(max_length=255, choices=MODEL_PERMISSION_CHOICES, verbose_name="Cấp quyền", null=True, blank=True)
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    @classmethod
    def get_display_fields(self):
        fields = ['user', 'sub_page', 'permission', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

class UserExtra(BaseModel):
    ROLE_CHOICES = (
        ('admin', 'Quản Lý Cao Cấp'),
        ('technician', 'Kỹ Thuật'),
        ('supervisor', 'Giám Sát'),
        ('normal_staff', 'Nhân Viên'),
    )
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default="normal_staff")
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    avatar = models.ImageField(upload_to='images/avatars/', blank=True, null=True)
    settings = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.user.username




class Task(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

class TaskUser(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)



class Project(BaseModel):
    STATUS_CHOICES = (
        ('not_started', 'Chưa bắt đầu'),
        ('done', 'Hoàn thành'),
        ('in_progress', 'Đang thực hiện'),
        ('pending', 'Tạm hoãn'),
        ('archived', 'Lưu trữ'),
    )

    name = models.CharField(max_length=1000, default="Dự án chưa được đặt tên")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="in_progress")
    description = models.TextField(blank=True, null=True, default='')
    image = models.ImageField(upload_to='images/projects/', blank=True, null=True, default='images/default/default_project.webp')
    users = models.ManyToManyField(User, through='ProjectUser')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    func_source = models.CharField(max_length=255, default="")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_number_of_jobs(self):
        return {
            'all': self.job_set.count(),
            'not_started': self.job_set.filter(status='not_started').count(),
            'done': self.job_set.filter(status='done').count(),
            'in_progress': self.job_set.filter(status='in_progress').count(),
            'pending': self.job_set.filter(status='pending').count(),
        }


class ProjectUser(BaseModel):
    ROLE_CHOICES = (
        ('view_only', 'Chỉ xem'),
        ('technician', 'Kỹ Thuật'),
        ('supervisor', 'Giám Sát'),
        ('all', 'Cấp tất cả quyền trong dự án'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Tài khoản", unique=True)
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default="view_only", verbose_name="Vị trí")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Dự án")
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    @classmethod
    def get_display_fields(self):
        fields = ['user', 'project', 'role', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class Job(SecondaryIDMixin, BaseModel):
    STATUS_CHOICES = (
        ('not_started', 'Chưa bắt đầu'),
        ('done', 'Hoàn thành'),
        ('in_progress', 'Đang thực hiện'),
        ('pending', 'Tạm hoãn'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="in_progress", verbose_name="Trạng thái")
    price_code = models.CharField(max_length=255, default="", verbose_name="Mã hiệu đơn giá")
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=1000, verbose_name="Tên công việc")
    category = models.CharField(max_length=1000, default="Chưa phân loại", verbose_name="Danh mục")
    unit = models.CharField(max_length=255, default="", verbose_name="Đơn vị")

    quantity = models.FloatField(default=0.0, validators=[MinValueValidator(0)], verbose_name="Khối lượng")
    unit_price = models.FloatField(default=0.0, validators=[MinValueValidator(0)], verbose_name="Đơn giá")
    total_amount = models.FloatField(default=0.0, validators=[MinValueValidator(0)], verbose_name="Thành tiền")

    description = models.TextField(blank=True, null=True, default='', verbose_name="Mô tả")
    start_date = models.DateField(default=timezone.now, verbose_name="Bắt đầu")
    end_date = models.DateField(default=timezone.now, verbose_name="Kết thúc")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['category', 'secondary_id']

    def clean(self):
        errors = ""

        # check if the job name is unique within the project
        # if the job is new

        if self._state.adding:
            if Job.objects.filter(project=self.project, name=self.name, category=self.category).exists():
                errors += ('- Trùng công việc và danh mục trong cùng dự án\n')

        # 1. Start date must be before or equal to the end date
        if self.start_date > self.end_date:
            errors += ('- Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc.\n')

        # End date must be before or equal to the project end date
        if pd.Timestamp(self.end_date) > pd.Timestamp(self.project.end_date):
            errors += (f'- Ngày kết thúc phải nhỏ hơn hoặc bằng ngày kết thúc dự án {self.project.end_date.strftime("%d/%m/%Y")}.\n')

        # 3. Ensure valid status
        valid_statuses = [choice[0] for choice in self.STATUS_CHOICES]
        if self.status not in valid_statuses:
            errors += (f'- Trạng thái "{self.status}" không hợp lệ.\n')

        # 5. Ensure required fields are not empty (even though they have blank=False)
        if not self.name:
            errors += ('- Tên công việc không được để trống.\n')
        if not self.unit:
            errors += ('- Đơn vị không được để trống.\n')
        if not self.unit_price:
            errors += ('- Đơn giá không được để trống.\n')
        if not self.quantity:
            errors += ('- Khối lượng không được để trống.\n')

        # 2. Ensure quantity and unit_price are non-negative
        try:
            if float(self.quantity) < 0:
                errors += ('- Khối lượng phải là số dương\n')
        except:
            errors += ('- Khối lượng phải là dạng số\n')
        try:
            if float(self.unit_price) < 0:
                errors += ('- Khối lượng phải là số dương\n')
        except:
            errors += ('- Khối lượng phải là dạng số\n')

        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)  # Call the original save method

    def get_jobplan_by_id(self, id):
        return JobPlan.objects.get(job=self, id=id)

    @classmethod
    def get_display_fields(self):
        fields = ['name', 'category', 'status', 'unit', 'quantity', 'unit_price', 'total_amount', 'start_date', 'end_date']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def __str__(self):
        return self.name



class JobPlan(BaseModel):
    STATUS_CHOICES = (
        ('wait_for_approval', 'Chờ phê duyệt'),
        ('approved', 'Đã phê duyệt'),
        ('rejected', 'Đã bị từ chối'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="wait_for_approval", verbose_name="Trạng thái")
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    plan_quantity = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    plan_amount = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    note = models.TextField(blank=True, null=True, default='')
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.plan_amount = self.plan_quantity * self.job.unit_price
        self.created_at = timezone.now()
        super().save(*args, **kwargs)  # Call the original save method

    def __str__(self):
        return f'Plan of {self.job} from {self.start_date} to {self.end_date}'


class JobDateReport(BaseModel):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    quantity = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    date_amount = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    note = models.TextField(blank=True, null=True, default='')
    created_at = models.DateTimeField(default=timezone.now)
    material = models.TextField(default='', verbose_name="Vật tư")  # Material
    labor = models.TextField(default='', verbose_name="Nhân công")   # Labor

    def save(self, *args, **kwargs):
        self.date_amount = self.quantity * self.job.unit_price
        super().save(*args, **kwargs)  # Call the original save method

    def __str__(self):
        return f'progress of {self.job} on {self.date}'


class VehicleType(BaseModel):
    class Meta:
        ordering = ['vehicle_type']
    vehicle_type = models.CharField(max_length=255, verbose_name="Loại xe", unique=True)
    note = models.TextField(blank=True, null=True, default='', verbose_name="Ghi chú")
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.vehicle_type

    @classmethod
    def get_display_fields(self):
        fields = ['vehicle_type', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class StaffData(BaseModel):
    STATUS_CHOICES = (
        ('active', 'Đang làm việc'),
        ('on_leave', 'Nghỉ phép'),
        ('resigned', 'Đã thôi việc'),
        ('terminated', 'Bị sa thải'),
    )
    POSITION_CHOICES = (
        ('manager', 'Quản lý'),
        ('staff', 'Nhân viên'),
        ('driver', 'Tài xế (chưa phân loại)'),
        ('driver_dumb_truck', 'Tài xế xe ben'),
        ('driver_road_roller', 'Tài xế xe lu'),
        ('driver_excavator', 'Tài xế xe cuốc'),
        ('driver_construction', 'Tài xế xe cơ giới khác'),
        
    )
    # Driver Information Fields
    full_name = models.CharField(max_length=255, verbose_name="Họ và tên", unique=True)
    hire_date = models.DateField(verbose_name="Ngày vào làm", default=timezone.now)
    identity_card = models.CharField(max_length=255, verbose_name="CCCD", default="")
    birth_year = models.DateField(verbose_name="Ngày sinh", default=timezone.now)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active', verbose_name="Trạng thái")
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, default='staff', verbose_name="Vị trí")
    # Bank Information
    bank_name = models.CharField(max_length=255, verbose_name="Ngân hàng", default="", blank=True)
    account_number = models.CharField(max_length=255, verbose_name="Số tài khoản", default="", blank=True)
    account_holder_name = models.CharField(max_length=255, verbose_name="Tên chủ tài khoản", default="", blank=True)
    # Contact Information
    phone_number = models.CharField(max_length=15, verbose_name="Số điện thoại", default="")
    address = models.CharField(max_length=255, verbose_name="Địa chỉ", default="")
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f'{self.full_name}'



    @classmethod
    def get_display_fields(self):
        fields = ['full_name', 'hire_date', 'status', 'position',
                  'identity_card', 'birth_year', 
                  'bank_name', 'account_number', 
                  'account_holder_name', 'phone_number', 'address']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields



class VehicleRevenueInputs(BaseModel):
    class Meta:
        ordering = ['vehicle_type']
    # Vehicle Information Fields
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, verbose_name="Loại xe")
    # Revenue Information Fields
    revenue_day_price = models.IntegerField(verbose_name="Đơn giá doanh thu", default=0, validators=[MinValueValidator(0)])
    
    # number of hours
    number_of_hours = models.IntegerField(verbose_name="Số giờ tính doanh thu", default=0, validators=[MinValueValidator(0)])

    # number of liters of oil per hour
    oil_consumption_liters_per_hour = models.IntegerField(verbose_name="Số lít dầu 1 tiếng", default=0, validators=[MinValueValidator(0)])

    # Resource Allocation Fields
    oil_consumption_per_hour = models.IntegerField(verbose_name="Định mức dầu 1 tiếng", default=0, validators=[MinValueValidator(0)])
    lubricant_consumption = models.IntegerField(verbose_name="Định mức nhớt", default=0, validators=[MinValueValidator(0)])
    insurance_fee = models.IntegerField(verbose_name="Định mức bảo hiểm", default=0, validators=[MinValueValidator(0)])
    road_fee_inspection = models.IntegerField(verbose_name="Định mức sử dụng đường bộ/Đăng kiểm", default=0, validators=[MinValueValidator(0)])
    tire_wear = models.IntegerField(verbose_name="Định mức hao mòn lốp xe", default=0, validators=[MinValueValidator(0)])
    police_fee = models.IntegerField(verbose_name="Định mức CA", default=0, validators=[MinValueValidator(0)])

    valid_from = models.DateField(verbose_name="Ngày bắt đầu áp dụng", default=timezone.now)

    note = models.CharField(max_length=255, verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f'{self.vehicle_type}'

    @classmethod
    def get_display_fields(self):
        fields = ['vehicle_type', 'revenue_day_price', 'number_of_hours', 'oil_consumption_liters_per_hour', 
                  'oil_consumption_per_hour', 'lubricant_consumption', 'insurance_fee', 'road_fee_inspection', 
                  'tire_wear', 'police_fee', 'valid_from', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields
    # todo: thêm fields chạy ngày, chạy đêm, tabo ngày, mỗi cái có đơn giá => tính phí vận chuyể

    @classmethod
    def get_valid_record(self, vehicle_type, date):
        date = get_valid_date(date)
        return VehicleRevenueInputs.objects.filter(valid_from__lte=date).order_by('-valid_from').first()


class DriverSalaryInputs(BaseModel):
    class Meta:
        ordering = ['driver']

    METHOD_CHOICES = (
        ('type_1', 'Nghỉ chủ nhật và lễ, nếu đi làm được tính thêm lương (xe lu)'),
        ('type_2', 'Không được nghỉ chủ nhật và lễ (xe cuốc)'),
    )

    driver = models.ForeignKey(StaffData, on_delete=models.CASCADE, verbose_name="Tài xế",
                               limit_choices_to={'position__icontains': 'driver'}, null=True)
    # Salary Fields 
    basic_month_salary = models.PositiveIntegerField(verbose_name="Lương cơ bản tháng", default=0)
    sunday_month_salary_percentage = models.FloatField(verbose_name="Hệ số lương tháng ngày chủ nhật", default=0.0)
    holiday_month_salary_percentage = models.FloatField(verbose_name="Hệ số lương tháng ngày lễ", default=0.0)
    calculation_method = models.CharField(max_length=10, choices=METHOD_CHOICES, verbose_name="Phương pháp tính lương", default='type_1')


    normal_hourly_salary = models.IntegerField(verbose_name="Lương theo giờ ngày thường", default=0)
    normal_overtime_hourly_salary = models.FloatField(verbose_name="Lương theo giờ tăng ca ngày thường", default=0)

    sunday_hourly_salary = models.IntegerField(verbose_name="Lương theo giờ chủ nhật", default=0)
    sunday_overtime_hourly_salary = models.FloatField(verbose_name="Lương theo giờ tăng ca chủ nhật", default=0)

    holiday_hourly_salary = models.IntegerField(verbose_name="Lương theo giờ ngày lễ", default=0)
    holiday_overtime_hourly_salary = models.FloatField(verbose_name="Lương theo giờ tăng ca ngày lễ", default=0)

    trip_salary = models.IntegerField(verbose_name="Lương theo chuyến", default=0)

    # Other Information
    fixed_allowance = models.PositiveIntegerField(verbose_name="Phụ cấp cố định", default=0)
    insurance_amount = models.PositiveIntegerField(verbose_name="Số tiền tham gia BHXH", default=0)

    valid_from = models.DateField(verbose_name="Ngày bắt đầu áp dụng", default=timezone.now)

    note = models.CharField(max_length=255, verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    @classmethod
    def get_display_fields(self):
        fields = ['driver', 'valid_from','basic_month_salary', 'sunday_month_salary_percentage', 
                  'holiday_month_salary_percentage', 'normal_hourly_salary', 'normal_overtime_hourly_salary', 
                  'sunday_hourly_salary', 'sunday_overtime_hourly_salary', 'holiday_hourly_salary', 
                  'holiday_overtime_hourly_salary', 'trip_salary', 'fixed_allowance', 'insurance_amount', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

 




class VehicleDetail(BaseModel):
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True, verbose_name="Loại xe")
    license_plate = models.CharField(max_length=255, verbose_name="Biển kiểm soát", default="",  unique=True)
    vehicle_name = models.CharField(max_length=255, verbose_name="Tên nhận dạng xe", default="")
    gps_name = models.CharField(max_length=255, verbose_name="Tên trên định vị", default="")
    vehicle_inspection_number = models.CharField(max_length=255, verbose_name="Số đăng kiểm")
    vehicle_inspection_due_date = models.DateField(verbose_name="Thời hạn đăng kiểm", default=timezone.now, null=True)  
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f'{self.vehicle_name} - {self.license_plate}'
    
    @classmethod
    def get_display_fields(self):
        fields = ['vehicle_type', 'license_plate', 'vehicle_name', 'gps_name', 
                  'vehicle_inspection_number', 'vehicle_inspection_due_date']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields









class DumbTruckPayRate(BaseModel):
    xe = models.ForeignKey(
        VehicleDetail,
        on_delete=models.SET_NULL, 
        null=True,
        limit_choices_to={'vehicle_type__vehicle_type': 'dump_truck'},
        verbose_name="Xe"
    )
    chay_ngay = models.PositiveIntegerField(verbose_name="Chạy ngày")
    chay_dem = models.PositiveIntegerField(verbose_name="Chạy đêm")
    tanbo_ngay = models.PositiveIntegerField(verbose_name="Tanbo ngày")
    tanbo_dem = models.PositiveIntegerField(verbose_name="Tanbo đêm")
    chay_xa = models.PositiveIntegerField(verbose_name="Chạy xa")
    keo_xe = models.PositiveIntegerField(verbose_name="Kéo xe")
    keo_xe_ngay_le = models.PositiveIntegerField(verbose_name="Kéo xe ngày lễ")
    chay_ngay_le = models.PositiveIntegerField(verbose_name="Chạy ngày lễ")
    tanbo_ngay_le = models.PositiveIntegerField(verbose_name="Tanbo ngày lễ")
    chay_xa_dem = models.PositiveIntegerField(verbose_name="Chạy xa đêm")
    luong_co_ban = models.PositiveIntegerField(verbose_name="Lương cơ bản")
    tanbo_cat_bc = models.PositiveIntegerField(verbose_name="Tanbo cát BC")
    tanbo_hh = models.PositiveIntegerField(verbose_name="Tanbo HH")
    chay_thue_sr = models.PositiveIntegerField(verbose_name="Chạy thuê SR")
    tanbo_cat_bc_dem = models.PositiveIntegerField(verbose_name="Tanbo cát BC đêm")
    tanbo_doi_3 = models.PositiveIntegerField(verbose_name="Tanbo Đội 3")
    chay_nhua = models.PositiveIntegerField(verbose_name="Chạy nhựa")
    chay_nhua_dem = models.PositiveIntegerField(verbose_name="Chạy nhựa đêm")
    keo_xe_dem = models.PositiveIntegerField(verbose_name="Kéo xe đêm")

    def __str__(self):
        return str(self.xe)

    @classmethod
    def get_display_fields(self):
        fields = ['xe', 'chay_ngay', 'chay_dem', 'tanbo_ngay', 'tanbo_dem', 'chay_xa',
                  'keo_xe', 'keo_xe_ngay_le', 'chay_ngay_le', 'tanbo_ngay_le', 'chay_xa_dem',
                  'luong_co_ban', 'tanbo_cat_bc', 'tanbo_hh', 'chay_thue_sr', 'tanbo_cat_bc_dem',
                  'tanbo_doi_3', 'chay_nhua', 'chay_nhua_dem', 'keo_xe_dem']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class DumbTruckRevenueData(BaseModel):
    # Choices for 'Loại chạy'
    LOAI_CHAY_CHOICES = [
        ('chay_ngay', 'Chạy ngày'),
        ('chay_dem', 'Chạy đêm'),
        ('chay_xa', 'Chạy xa'),
        ('tanbo_ngay', 'Tanbo ngày'),
        ('tanbo_dem', 'Tanbo đêm'),
    ]

    # Choices for 'Cách tính'
    CACH_TINH_CHOICES = [
        ('tren_1_km', 'Trên 1 km'),
        ('tren_chuyen', 'Trên chuyến'),
    ]

    # Choices for 'Loại vật tư'
    LOAI_VAT_TU_CHOICES = [
        ('khong_vat_tu', 'Không vật tư'),
        ('cat_dat_da', 'Cát, đá, đất'),
        ('vat_tu_khac', 'Vật tư khác'),
    ]

    # Choices for 'Mốc'
    MOC_CHOICES = [
        ('moc_1_20km', 'Mốc 1 (0-20km)'),
        ('moc_2_35km', 'Mốc 2 (0-35)'),
        ('moc_3_55km', 'Mốc 3 (0-55)'),
    ]

    # Choices for 'Kích cỡ xe'
    KICH_CO_XE_CHOICES = [
        ('xe_nho', 'Xe nhỏ'),
        ('xe_lon', 'Xe lớn'),
    ]

    loai_chay = models.CharField(
        max_length=255, choices=LOAI_CHAY_CHOICES, verbose_name="Loại chạy"
    )
    cach_tinh = models.CharField(
        max_length=255, choices=CACH_TINH_CHOICES, verbose_name="Cách tính"
    )
    loai_vat_tu = models.CharField(
        max_length=255, choices=LOAI_VAT_TU_CHOICES, verbose_name="Loại vật tư"
    )
    moc = models.CharField(max_length=255, choices=MOC_CHOICES, verbose_name="Mốc")
    kich_co_xe = models.CharField(
        max_length=255, choices=KICH_CO_XE_CHOICES, verbose_name="Kích cỡ xe"
    )
    don_gia = models.PositiveIntegerField(verbose_name="Đơn giá")

    def __str__(self):
        return f"{self.loai_chay} - {self.kich_co_xe}"
    @classmethod
    def get_display_fields(self):
        fields = ['loai_chay', 'cach_tinh', 'loai_vat_tu', 'moc', 'kich_co_xe', 'don_gia']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class Location(BaseModel):
    TYPE_OF_LOCATION_CHOICES = [
        ('du_an', 'Dự án/công trình'),
        ('kho_noi_bo', 'Kho nội bộ'),
        ('bat_dong_san_noi_bo', 'Bất động sản nội bộ'),
        ('khach_hang_dau_ra', 'Khách hàng đầu ra'),
        ('khach_hang_dau_vao', 'Khách hàng đầu vào'),
    ]

    name = models.CharField(max_length=500, verbose_name="Tên địa điểm")
    address = models.CharField(max_length=1000, verbose_name="Địa chỉ")
    type_of_location = models.CharField(max_length=255, choices=TYPE_OF_LOCATION_CHOICES, verbose_name="Loại hình")
    created_at = models.DateTimeField(default=timezone.now)

    @classmethod
    def get_display_fields(self):
        fields = ['name', 'address', 'type_of_location']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields
    
    def __str__(self):
        return self.name



# Model báo cáo chuyến (file báo cáo xe ben tháng 8)
# trong báo cáo chuyến, có điểm đến, điểm đi (chọn từ database)
# điểm đến điểm đi là một bảng danh sách các nơi



class NormalWorkingTime(BaseModel):
    # gotta get valid normal working time based on the valid date so that old data can be updated (from a button click manually)
    class Meta:
        ordering = ['-valid_from']
    morning_start = models.TimeField(verbose_name="Bắt đầu ca sáng", default=time(7, 30))
    morning_end = models.TimeField(verbose_name="Kết thúc ca sáng", default=time(11, 30))
    afternoon_start = models.TimeField(verbose_name="Bắt đầu ca chiều", default=time(13, 0))
    afternoon_end = models.TimeField(verbose_name="Kết thúc ca chiều", default=time(17, 0))
    # Valid from
    valid_from = models.DateField(verbose_name="Ngày bắt đầu áp dụng")
    note = models.TextField(verbose_name="Ghi chú", default="")
    created_at = models.DateTimeField(default=timezone.now)
    @classmethod
    def get_display_fields(self):
        fields = ['morning_start', 'morning_end', 'afternoon_start', 'afternoon_end', 'valid_from', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    @classmethod
    def get_valid_normal_working_time(self):
        # get the last valid working time
        normal_working_time = NormalWorkingTime.objects.all().order_by('valid_from').last()
        if normal_working_time:
            return normal_working_time.morning_start, normal_working_time.morning_end, normal_working_time.afternoon_start, normal_working_time.afternoon_end
        else:
            # default working time
            morning_start = time(7, 30)
            morning_end = time(11, 30)
            afternoon_start = time(13, 0)
            afternoon_end = time(17, 0)
            return morning_start, morning_end, afternoon_start, afternoon_end
    def clean(self):
        errors = ""
        # if morning end is before morning start
        if self.morning_end < self.morning_start:
            errors += ('- Bắt đầu ca sáng phải nhỏ hơn hoặc bằng kết thúc ca sáng.\n')
        # if afternoon end is before afternoon start
        if self.afternoon_end < self.afternoon_start:
            errors += ('- Bắt đầu ca chiều phải nhỏ hơn hoặc bằng kết thúc ca chiều.\n')
        # if afternoon start is before morning end
        if self.afternoon_start < self.morning_end:
            errors += ('- Bắt đầu ca chiều phải nhỏ hơn hoặc bằng kết thúc ca sáng.\n')
        if errors:
            raise ValidationError(errors)



class Holiday(BaseModel):  
    class Meta:
        ordering = ['-date']
    date = models.DateField(verbose_name="Ngày lễ",  unique=True)
    note = models.TextField(verbose_name="Ghi chú", default="")
    created_at = models.DateTimeField(default=timezone.now)
    @classmethod
    def get_display_fields(self):
        fields = ['date', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields
    @classmethod
    def is_holiday(self, date):
        # check if the date is holiday
        holiday = Holiday.objects.filter(date=date).first()
        if holiday:
            return True
        else:
            return False

        


class VehicleOperationRecord(BaseModel):

    SOURCE_CHOICES = [
        ('gps', 'GPS'),
        ('manual', 'Nhập tay'),
    ]
    TYPE_CHOICES = [
        ('plus', 'Cộng'),
        ('minus', 'Trừ'),
    ]

    class Meta:
        ordering = ['vehicle', 'start_time']

    vehicle = models.CharField(max_length=20, verbose_name="Xe")
    driver = models.ForeignKey(StaffData, on_delete=models.SET_NULL, verbose_name="Tài xế",
                               limit_choices_to={'position__icontains': 'driver'}, null=True)
    start_time = models.DateTimeField(verbose_name="Thời điểm mở máy", null=True, blank=True)
    end_time = models.DateTimeField(verbose_name="Thời điểm tắt máy", null=True, blank=True)
    duration_seconds = models.IntegerField(verbose_name="Thời gian hoạt động", default= 0)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Địa điểm")
    overtime = models.IntegerField(verbose_name="Thời gian tăng ca", default=0)
    normal_working_time = models.IntegerField(verbose_name="Thời gian làm hành chính", default=0)
    fuel_allowance = models.IntegerField(verbose_name="Phụ cấp xăng", default=0)
    image = models.ImageField(upload_to='images/vehicle_operations/', verbose_name="Hình ảnh", default='', null=True, blank=True)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, verbose_name="Nguồn dữ liệu", default='gps')
    note = models.TextField(verbose_name="Ghi chú", default='')
    
    # add over time
    allow_overtime = models.BooleanField(verbose_name="Cho phép tính lương tăng ca", default=False)


    def __str__(self):
        return self.vehicle
    
    @classmethod
    def get_display_fields(self):
        fields = ['vehicle', 'start_time', 'end_time', 'duration_seconds', 'source', 
                  'driver', 'location', 'normal_working_time', 'overtime', 'allow_overtime', 'fuel_allowance', 'image', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields
    def get_driver_choices(self):
        drivers = StaffData.objects.filter(position__icontains='driver')
        # return a dict of choices with key id and name
        dict_drivers = [{'id': driver.id, 'name':driver.full_name} for driver in drivers]
        return dict_drivers

    def get_location_choices(self):
        locations = Location.objects.all()
        # return a dict of choices with key id and name
        dict_locations = [{'id': location.id, 'name':location.name} for location in locations]
        return dict_locations


    def calculate_working_time(self):
        if self.source != 'gps':
            return self.normal_working_time, self.overtime
        
        start_time = self.start_time
        end_time = self.end_time
        # Define the working hours
        morning_start, morning_end, afternoon_start, afternoon_end = NormalWorkingTime.get_valid_normal_working_time()

        # get the set of seconds of the working hours
        the_order_of_second_of_morning_start = morning_start.hour * 3600 + morning_start.minute * 60 + morning_start.second
        the_order_of_second_of_morning_end = morning_end.hour * 3600 + morning_end.minute * 60 + morning_end.second
        the_order_of_second_of_afternoon_start = afternoon_start.hour * 3600 + afternoon_start.minute * 60 + afternoon_start.second
        the_order_of_second_of_afternoon_end = afternoon_end.hour * 3600 + afternoon_end.minute * 60 + afternoon_end.second

        # The set of all seconds working hours
        all_seconds_of_morning = set(range(the_order_of_second_of_morning_start, the_order_of_second_of_morning_end))
        all_seconds_of_afternoon = set(range(the_order_of_second_of_afternoon_start, the_order_of_second_of_afternoon_end))
        all_seconds_of_working_hours = all_seconds_of_morning | all_seconds_of_afternoon

        # The set of all seconds from start_time to end_time
        the_order_of_second_of_start_time = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
        the_order_of_second_of_end_time = end_time.hour * 3600 + end_time.minute * 60 + end_time.second
        all_seconds_from_start_to_end = set(range(the_order_of_second_of_start_time, the_order_of_second_of_end_time))

        # The set of seconds that is overtime
        overtime = all_seconds_from_start_to_end - all_seconds_of_working_hours
        # count the number of seconds
        if overtime:
            normal_working_time = self.duration_seconds - len(overtime)
            self.normal_working_time = normal_working_time
            self.overtime = len(overtime)
            return normal_working_time, len(overtime)
        else:
            normal_working_time = self.duration_seconds
            self.normal_working_time = normal_working_time
            self.overtime = 0
            return normal_working_time, 0


class LiquidUnitPrice(BaseModel):
    TYPE_CHOICES = [
        ('diesel', 'Dầu diesel (lít)'),
        ('gasoline', 'Xăng (lít)'),

        ('lubricant_10', 'Nhớt thủy lực (lít)'),

        ('lubricant_engine', 'Nhớt máy xe cơ giới (lít)'),
        ('lubricant_engine_dumbtruck', 'Nhớt máy xe ben (lít)'),

        ('lubricant_140_thick', 'Nhớt 140 đặc (lít)'),
        ('lubricant_140', 'Nhớt 140 lỏng (lít)'),

        ('grease', 'Mỡ bò xe cơ giới (lít)'),
        ('grease_dumbtruck', 'Mỡ bò xe ben (lít)'),
    ]
    liquid_type = models.CharField(max_length=100, choices=TYPE_CHOICES, verbose_name="Loại")
    unit_price = models.IntegerField(verbose_name="Đơn giá", default=0, validators=[MinValueValidator(0)])
    valid_from = models.DateField(verbose_name="Ngày bắt đầu áp dụng", default=timezone.now)
    note = models.TextField(verbose_name="Ghi chú", default="")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.liquid_type}"

    @classmethod
    def get_display_fields(self):
        fields = ['liquid_type', 'unit_price', 'unit', 'valid_from', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    @classmethod
    def get_unit_price(self, liquid_type, date):
        print(">>>>>>>>>>>>>>>>>>", liquid_type, date)
        liquid_unit_price = LiquidUnitPrice.objects.filter(liquid_type=liquid_type, valid_from__lte=date).order_by('-valid_from').first()
        return liquid_unit_price

    def save(self):
        super().save()
        # recalculate all FillingRecord which liquid_type = liquid_type
        filling_records = FillingRecord.objects.filter(liquid_type=self.liquid_type)
        for filling_record in filling_records:
            filling_record.calculate_total_amount()
            filling_record.save()



class FillingRecord(BaseModel):
    TYPE_CHOICES = [
        ('diesel', 'Dầu diesel (lít)'),
        ('gasoline', 'Xăng (lít)'),

        ('lubricant_10', 'Nhớt thủy lực (lít)'),

        ('lubricant_engine', 'Nhớt máy xe cơ giới (lít)'),
        ('lubricant_engine_dumbtruck', 'Nhớt máy xe ben (lít)'),

        ('lubricant_140_thick', 'Nhớt 140 đặc (lít)'),
        ('lubricant_140', 'Nhớt 140 lỏng (lít)'),

        ('grease', 'Mỡ bò xe cơ giới (lít)'),
        ('grease_dumbtruck', 'Mỡ bò xe ben (lít)'),
    ]
    liquid_type = models.CharField(max_length=100, choices=TYPE_CHOICES, verbose_name="Loại")
    vehicle = models.ForeignKey(VehicleDetail, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Xe")
    quantity = models.FloatField(verbose_name="Số lượng")
    total_amount = models.IntegerField(verbose_name="Thành tiền", default=0, validators=[MinValueValidator(0)])
    fill_date = models.DateField(verbose_name="Ngày đổ", default=timezone.now)
    note = models.TextField(verbose_name="Ghi chú", default="")
    created_at = models.DateTimeField(default=timezone.now)

    def save(self):
        self.calculate_total_amount()
        super().save()

    @classmethod
    def get_display_fields(self):
        fields = ['liquid_type', 'vehicle', 'quantity', 'total_amount', 'fill_date', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def calculate_total_amount(self):
        # Get Unit Price
        unit_price = LiquidUnitPrice.get_unit_price(self.liquid_type, self.fill_date)
        if unit_price:
            self.total_amount = self.quantity * unit_price.unit_price
        else:
            self.total_amount = 0


class FuelFillingRecord(BaseModel):
    vehicle = models.ForeignKey(VehicleDetail, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Xe")
    litter = models.FloatField(verbose_name="Số lít")
    unit_price = models.IntegerField(verbose_name="Đơn giá", default=0, validators=[MinValueValidator(0)])
    total_amount = models.IntegerField(verbose_name="Thành tiền", default=0, validators=[MinValueValidator(0)])
    
    fill_date = models.DateField(verbose_name="Ngày đổ nhiên liệu", default=timezone.now)
    note = models.TextField(verbose_name="Ghi chú", default="")
    created_at = models.DateTimeField(default=timezone.now)

    def save(self):
        self.total_amount = self.litter * self.unit_price
        super().save()

    @classmethod
    def get_display_fields(self):
        fields = ['vehicle', 'litter', 'unit_price', 'total_amount', 'fill_date', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields
    
    def __str__(self):
        return f'{self.vehicle} - {self.fill_date}'

class LubeFillingRecord(BaseModel):
    vehicle = models.ForeignKey(VehicleDetail, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Xe")
    litter = models.FloatField(verbose_name="Số lít")
    unit_price = models.IntegerField(verbose_name="Đơn giá", default=0, validators=[MinValueValidator(0)])
    total_amount = models.IntegerField(verbose_name="Thành tiền", default=0, validators=[MinValueValidator(0)])
    
    fill_date = models.DateField(verbose_name="Ngày đổ nhớt", default=timezone.now)
    note = models.TextField(verbose_name="Ghi chú", default="")
    created_at = models.DateTimeField(default=timezone.now)

    def save(self):
        self.total_amount = self.litter * self.unit_price
        super().save()

    @classmethod
    def get_display_fields(self):
        fields = ['vehicle', 'litter', 'unit_price', 'total_amount', 'fill_date', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields
    
    def __str__(self):
        return f'{self.vehicle} - {self.fill_date}'

class VehicleDepreciation(BaseModel):
    vehicle = models.ForeignKey(VehicleDetail, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Xe")
    depreciation_amount = models.IntegerField(verbose_name="Khấu hao theo ngày", default=0, validators=[MinValueValidator(0)])
    from_date = models.DateField(verbose_name="Ngày bắt đầu", default=timezone.now)
    to_date = models.DateField(verbose_name="Ngày kết thúc", default=timezone.now)
    note = models.TextField(verbose_name="Ghi chú", default="")
    created_at = models.DateTimeField(default=timezone.now)

    @classmethod
    def get_vehicle_depreciation(cls, vehicle, date):
        try:
            records = cls.objects.filter(vehicle=vehicle, from_date__lte=date, to_date__gte=date)
            # get the latest record
            records.order_by('-created_at')
            return records.first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_display_fields(self):
        fields = ['vehicle', 'depreciation_amount', 'from_date', 'to_date', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields
    
    def __str__(self):
        return f'{self.vehicle} - {self.from_date} - {self.to_date}'

class VehicleBankInterest(BaseModel):
    vehicle = models.ForeignKey(VehicleDetail, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Xe")
    interest_amount = models.IntegerField(verbose_name="Lãi suất theo ngày", default=0, validators=[MinValueValidator(0)])
    from_date = models.DateField(verbose_name="Ngày bắt đầu", default=timezone.now)
    to_date = models.DateField(verbose_name="Ngày kết thúc", default=timezone.now)
    note = models.TextField(verbose_name="Ghi chú", default="")
    created_at = models.DateTimeField(default=timezone.now)

    @classmethod
    def get_vehicle_bank_interest(cls, vehicle, date):
        try:
            records = cls.objects.filter(vehicle=vehicle, from_date__lte=date, to_date__gte=date)
            # get the latest record
            records.order_by('-created_at')
            return records.first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_display_fields(self):
        fields = ['vehicle', 'interest_amount', 'from_date', 'to_date', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields
    
    def __str__(self):
        return f'{self.vehicle} - {self.from_date} - {self.to_date}'



class VehicleMaintenance(BaseModel):
    MAINTENANCE_CATEGORY_CHOICES = (
        ('periodic_check', 'Kiểm tra định kì'),
        ('repair', 'Sửa chữa hư hỏng'),
    )
    
    APPROVAL_STATUS_CHOICES = (
        ('scratch', 'Bảng nháp'),
        ('wait_for_approval', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('need_update', 'Cần sửa lại'),
        ('rejected', 'Từ chối'),
    )

    RECEIVED_STATUS_CHOICES = (
        ('received', 'Đã nhận'),
        ('not_received', 'Chưa nhận'),
    )

    PAID_STATUS_CHOICES = (
        ('paid', 'Đã T.toán'),
        ('not_paid', 'Chưa T.toán'),
    )

    DONE_STATUS_CHOICES = (
        ('done', 'Xong'),
        ('not_done', 'Chưa xong'),
    )

    class Meta:
        ordering = ['-created_at']

    repair_code = models.CharField(max_length=255, verbose_name="Mã phiếu sửa chữa", default="", null=True, blank=True)
    vehicle = models.ForeignKey(VehicleDetail, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Xe")
    maintenance_amount = models.IntegerField(verbose_name="Chi phí", default=0, validators=[MinValueValidator(0)])
    maintenance_category = models.CharField(max_length=255, choices=MAINTENANCE_CATEGORY_CHOICES, verbose_name="Phân loại", default="", null=True, blank=True)
    from_date = models.DateField(verbose_name="Ngày nhận sửa chữa", default=timezone.now)
    to_date = models.DateField(verbose_name="Ngày xong sửa chữa", default=timezone.now)

    approval_status = models.CharField(max_length=50, choices=APPROVAL_STATUS_CHOICES, default='scratch', verbose_name="Duyệt")
    received_status = models.CharField(max_length=50, choices=RECEIVED_STATUS_CHOICES, default='not_received', verbose_name="Nhận hàng")
    paid_status = models.CharField(max_length=50, choices=PAID_STATUS_CHOICES, default='not_paid', verbose_name="Thanh toán")
    done_status = models.CharField(max_length=50, choices=DONE_STATUS_CHOICES, default='not_done', verbose_name="Sửa chữa")

    note = models.TextField(verbose_name="Ghi chú", default="")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo phiếu")

    def save(self):
        super().save()
        self.repair_code = "SC" + str(self.pk).zfill(4)
        # Get all related vehicle parts
        vehicle_parts = VehicleMaintenanceRepairPart.objects.filter(vehicle_maintenance=self)
        # Calculate the total maintenance amount
        total_amount = 0
        for vehicle_part in vehicle_parts:
            part_amount = vehicle_part.repair_part.part_price * vehicle_part.quantity
            total_amount += part_amount

        self.maintenance_amount = total_amount

        
        # Check if all parts are received, if yes => received_status = 'received'
        if vehicle_parts.filter(received_status='not_received').count() == 0:
            self.received_status = 'received'
        else:
            self.received_status = 'not_received'
        # Check if all parts are paid, if yes => paid_status = 'paid'
        if vehicle_parts.filter(paid_status='not_paid').count() == 0:
            self.paid_status = 'paid'
        else:
            self.paid_status = 'not_paid'
        # Check if all parts are done, if yes => done_status = 'done'
        if vehicle_parts.filter(done_status='not_done').count() == 0:
            self.done_status = 'done'
        else:
            self.done_status = 'not_done'
        super().save()



        # Create or update payment records
        if self.approval_status == 'approved' or True:
            all_provider_payment_state = self.calculate_all_provider_payment_states()
            
            # Get all payment records which has vehicle_maintenance = self and provider_id = provider_id
            for provider_id in all_provider_payment_state:
                payment_records = PaymentRecord.objects.filter(vehicle_maintenance=self, provider_id=provider_id).order_by('id')
                if len(payment_records) == 0:
                    payment_record, created = PaymentRecord.objects.get_or_create(vehicle_maintenance=self, provider_id=provider_id)
                    payment_record.previous_debt = all_provider_payment_state[provider_id]['debt_amount']
                    payment_record.purchase_amount = all_provider_payment_state[provider_id]['purchase_amount']
                    payment_record.save()
                else:
                    total_transferred_amount = 0
                    previous_record = None
                    purchase_amount = all_provider_payment_state[provider_id]['purchase_amount']
                    for payment_record in payment_records:
                        total_transferred_amount += previous_record.transferred_amount if previous_record else 0
                        previous_record = payment_record
                        previous_debt = purchase_amount - total_transferred_amount
                        payment_record.previous_debt = previous_debt
                        payment_record.purchase_amount = all_provider_payment_state[provider_id]['purchase_amount']
                        payment_record.debt = previous_debt - payment_record.transferred_amount
                        payment_record.save()



        elif self.approval_status == 'rejected':
            PaymentRecord.objects.filter(vehicle_maintenance=self).delete()

    def calculate_all_provider_payment_states(self):
        # get all the parts in this vehicle maintenance
        vehicle_parts = VehicleMaintenanceRepairPart.objects.filter(vehicle_maintenance=self)
        # get all the providers in this vehicle maintenance
        provider_ids = vehicle_parts.values_list('repair_part__part_provider', flat=True).distinct()
        provider_ids = set(provider_ids)
        all_provider_payment_state = {}
        for provider_id in provider_ids:
            provider = PartProvider.objects.get(pk=provider_id)
            # calculate the purchase amount
            purchase_amount = 0
            provider_vehicle_parts = vehicle_parts.filter(repair_part__part_provider=provider)
            for provider_vehicle_part in provider_vehicle_parts:
                purchase_amount += provider_vehicle_part.repair_part.part_price * provider_vehicle_part.quantity

            # calculate the transferred amount
            transferred_amount = 0
            payment_records = PaymentRecord.objects.filter(vehicle_maintenance=self, provider=provider)
            for payment_record in payment_records:
                transferred_amount += payment_record.transferred_amount

            # calculate the debt amount
            debt_amount = purchase_amount - transferred_amount

            state = {
                'purchase_amount': purchase_amount,
                'transferred_amount': transferred_amount,
                'debt_amount': debt_amount
            }
            all_provider_payment_state[provider.id] = state 
        return all_provider_payment_state

    @classmethod
    def get_vehicle_maintenance_records(cls, vehicle, date):
        try:
            records = cls.objects.filter(vehicle=vehicle, to_date=date)
            return records
        except cls.DoesNotExist:
            return None

    def get_vehicle_part_list(self):
        vehicle_parts = VehicleMaintenanceRepairPart.objects.filter(vehicle_maintenance=self, repair_part__isnull=False)
        # Put into dict of groups of providers
        vehicle_parts_dict = {}
        for vehicle_part in vehicle_parts:
            if vehicle_part.repair_part.part_provider not in vehicle_parts_dict:
                vehicle_parts_dict[vehicle_part.repair_part.part_provider] = []
            vehicle_parts_dict[vehicle_part.repair_part.part_provider].append(vehicle_part)
        return vehicle_parts_dict

    @classmethod
    def get_repair_part_list(cls):
        part_list = RepairPart.objects.all()
        return part_list

    @classmethod
    def get_display_fields(self):
        fields = ['repair_code', 'vehicle', 'maintenance_category', 'approval_status', 'received_status', 'paid_status', 'done_status', 'maintenance_amount', 'from_date', 'to_date', 'created_at']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def __str__(self):
        return self.repair_code

class MaintenanceImage(BaseModel):
    vehicle_maintenance = models.ForeignKey(VehicleMaintenance, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Phiếu sửa chữa")
    image = models.ImageField(upload_to='maintenance/', verbose_name="Hình ảnh", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f'{self.vehicle_maintenance}'

class PartProvider(BaseModel):
    # Driver Information Fields
    name = models.CharField(max_length=255, verbose_name="Tên nhà cung cấp", unique=True)
    # Bank Information
    bank_name = models.CharField(max_length=255, verbose_name="Ngân hàng", default="", blank=True)
    account_number = models.CharField(max_length=255, verbose_name="Số tài khoản", default="", blank=True)
    account_holder_name = models.CharField(max_length=255, verbose_name="Tên chủ tài khoản", default="", blank=True)

    # Fianance
    total_purchase_amount = models.IntegerField(verbose_name="Tổng tiền mua", default=0, validators=[MinValueValidator(0)])
    total_transferred_amount = models.IntegerField(verbose_name="Tổng thanh toán", default=0, validators=[MinValueValidator(0)])
    total_outstanding_debt = models.IntegerField(verbose_name="Tổng công nợ", default=0, validators=[MinValueValidator(0)])
    
    # Contact Information
    phone_number = models.CharField(max_length=15, verbose_name="Số điện thoại", default="")
    address = models.CharField(max_length=255, verbose_name="Địa chỉ", default="")
    note = models.TextField(verbose_name="Ghi chú", default="")
    created_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f'{self.name}'
    @classmethod
    def get_display_fields(self):
        fields = ['name', 'phone_number', 'address', 'bank_name', 'account_number', 'account_holder_name', 
            'total_purchase_amount', 'total_transferred_amount', 'total_outstanding_debt' ,'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def calculate_payment_states(self):
        # Get all VehicleMaintenanceRepairPart
        repair_parts = VehicleMaintenanceRepairPart.objects.filter(repair_part__part_provider=self)
        # Calculate the purchase amount
        purchase_amount = 0
        for repair_part in repair_parts:
            purchase_amount += repair_part.repair_part.part_price * repair_part.quantity

        # Calculate the transferred amount
        transferred_amount = 0
        payment_records = PaymentRecord.objects.filter(provider=self)
        for payment_record in payment_records:
            transferred_amount += payment_record.transferred_amount

        # Calculate the debt amount
        debt_amount = purchase_amount - transferred_amount

        self.total_purchase_amount = purchase_amount
        self.total_transferred_amount = transferred_amount
        self.total_outstanding_debt = debt_amount
        self.save()



class RepairPart(BaseModel):
    class Meta:
        ordering = ['vehicle_type', 'part_price']
    part_provider = models.ForeignKey(PartProvider, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Nhà cung cấp")
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Loại xe")
    part_number = models.CharField(max_length=255, verbose_name="Mã phụ tùng", unique=True)
    part_name = models.CharField(max_length=255, verbose_name="Tên đầy đủ")
    part_price = models.IntegerField(verbose_name="Đơn giá", default=0, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=255, verbose_name="Đơn vị", default="cái", null=True, blank=True)
    image = models.ImageField(verbose_name="Hình ảnh", default="", null=True, blank=True)
    note = models.TextField(verbose_name="Mô tả", default="", null=True, blank=True)
    valid_from = models.DateField(verbose_name="Ngày áp dụng", default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f'{self.part_number} - {self.part_name}'

    @classmethod
    def get_display_fields(self):
        fields = ['part_provider', 'part_number', 'part_name', 'part_price', 'image', 'note', 'valid_from']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class VehicleMaintenanceRepairPart(BaseModel):

    RECEIVED_STATUS_CHOICES = (
        ('received', 'Đã nhận'),
        ('not_received', 'Chưa nhận'),
    )

    PAID_STATUS_CHOICES = (
        ('paid', 'Đã T.toán'),
        ('not_paid', 'Chưa T.toán'),
    )

    DONE_STATUS_CHOICES = (
        ('done', 'Xong'),
        ('not_done', 'Chưa xong'),
    )

    vehicle_maintenance = models.ForeignKey(VehicleMaintenance, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Phiếu sửa chữa")
    repair_part = models.ForeignKey(RepairPart, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Bộ phận")
    quantity = models.IntegerField(verbose_name="Số lượng", default=0, validators=[MinValueValidator(0)])
    received_status = models.CharField(max_length=50, choices=RECEIVED_STATUS_CHOICES, default='not_received', verbose_name="Trạng thái nhận hàng")
    paid_status = models.CharField(max_length=50, choices=PAID_STATUS_CHOICES, default='not_paid', verbose_name="Trạng thái thanh toán")
    done_status = models.CharField(max_length=50, choices=DONE_STATUS_CHOICES, default='not_done', verbose_name="Trạng thái xong sửa chữa")
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        provider = self.repair_part.part_provider
        provider.calculate_payment_states()

    @classmethod
    def get_maintenance_amount(cls, vehicle, from_date, to_date):
        total_amount = 0
        vehicle_maintenances = VehicleMaintenance.objects.filter(
            vehicle=vehicle, from_date__gte=from_date, from_date__lte=to_date)
        for vehicle_maintenance in vehicle_maintenances:
            repair_parts = VehicleMaintenanceRepairPart.objects.filter(
                vehicle_maintenance=vehicle_maintenance)
            for repair_part in repair_parts:
                if repair_part.received_status == 'received':
                    total_amount += repair_part.repair_part.part_price * repair_part.quantity

        return total_amount

class PaymentRecord(BaseModel):
    class Meta:
        ordering = ['vehicle_maintenance', 'provider', '-id']

    PAID_STATUS_CHOICES = (
        ('not_requested', 'Chưa đề nghị'),
        ('requested', 'Đề nghị T.toán'),
        ('partial_paid', 'T.toán một phần'),
        ('paid', 'Đã T.toán đủ'),
    )
    vehicle_maintenance = models.ForeignKey(VehicleMaintenance, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Phiếu sửa chữa")
    provider = models.ForeignKey(PartProvider, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Nhà cung cấp")
    status = models.CharField(max_length=50, choices=PAID_STATUS_CHOICES, default='not_requested', verbose_name="Trạng thái thanh toán")

    purchase_amount= models.IntegerField(verbose_name="Tổng tiền trên phiếu sửa chữa", default=0, validators=[MinValueValidator(0)])
    previous_debt = models.IntegerField(verbose_name="Nợ kì trước", default=0, validators=[MinValueValidator(0)])

    requested_amount = models.IntegerField(verbose_name="Số tiền đề nghị", default=0, validators=[MinValueValidator(0)])
    requested_date = models.DateField(verbose_name="Ngày đề nghị", default=timezone.now)

    transferred_amount = models.IntegerField(verbose_name="Tiền thanh toán", default=0, validators=[MinValueValidator(0)])
    payment_date = models.DateField(verbose_name="Ngày thanh toán", default=timezone.now)   

    debt = models.IntegerField(verbose_name="Nợ còn lại", default=0, validators=[MinValueValidator(0)])

    lock = models.BooleanField(verbose_name="Khóa phiếu", default=False)

    image1 = models.ImageField(verbose_name="Hình ảnh", upload_to='images/finance/', blank=True, null=True)
    image2 = models.ImageField(verbose_name="Hình ảnh", upload_to='images/finance/', blank=True, null=True)

    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f'{self.vehicle_maintenance} - {self.payment_date}'

    @classmethod
    def get_display_fields(self):
        fields = ['vehicle_maintenance', 'provider', 'status', 'lock', 'purchase_amount', 
            'previous_debt', 'requested_amount', 'requested_date', 'transferred_amount', 
            'payment_date', 'debt', 'note', 'image1']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields
    
    def save(self, *args, **kwargs):
        # Delete to test
        # print("Delete payment records")
        # payment_records = PaymentRecord.objects.all().delete()
        if self.requested_amount > 0:
            self.status = 'requested'

        if self.transferred_amount > 0 and self.transferred_amount < self.previous_debt:
            self.status = 'partial_paid'
            self.debt = self.previous_debt - self.transferred_amount

        if self.transferred_amount > 0 and self.transferred_amount == self.previous_debt:
            self.status = 'paid'
            self.debt = self.previous_debt - self.transferred_amount

        if self.requested_amount == 0:
            self.status = 'not_requested'


        super().save(*args, **kwargs)
        self.provider.calculate_payment_states()
        
        # extract the vehicle maintenance and provider
        vehicle_maintenance = self.vehicle_maintenance
        provider = self.provider
        # get all payment records
        last_payment_record = PaymentRecord.objects.filter(vehicle_maintenance=vehicle_maintenance, provider=provider).order_by('id').last()
        # if self = last payment record
        if last_payment_record == self and self.lock == True and self.debt != 0:
            # create new payment record
            new_payment_record = PaymentRecord.objects.create(vehicle_maintenance=vehicle_maintenance, provider=provider)
            new_payment_record.previous_debt = self.debt
            new_payment_record.purchase_amount = self.purchase_amount
            new_payment_record.debt = self.debt
            new_payment_record.save()



    def clean(self):
        errors = ""
        if self.requested_amount > self.previous_debt:
            errors += (f'- Số tiền đề nghị phải nhỏ hơn hoặc bằng nợ kì trước {format(self.previous_debt, ",d")}.\n')

        if self.requested_amount==0 and self.transferred_amount > 0:
            errors += (f'-Chưa thanh toán khi chưa có đề nghị.\n')

        if self.transferred_amount < self.requested_amount and self.transferred_amount > 0:
            errors += (f'- Số tiền thanh toán phải lớn hơn hoặc bằng số tiền đề nghị {format(self.requested_amount, ",d")}.\n')
        if self.transferred_amount > self.previous_debt:
            errors += (f'- Số tiền thanh toán phải nhỏ hơn hoặc bằng nợ kì trước {format(self.previous_debt, ",d")}.\n')
        if self.payment_date < self.requested_date:
            errors += (f'- Ngày thanh toán phải lớn hơn hoặc bằng ngày đề nghị {self.requested_date.strftime("%d/%m/%Y")}.\n')
        
        if self.lock and self.transferred_amount == 0:
            errors += (f'- Không thể khóa phiếu thanh toán khi chưa thanh toán.\n')

        if errors:
            raise ValidationError(errors)
    