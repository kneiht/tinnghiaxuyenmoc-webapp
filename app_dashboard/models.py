import time, re, io
from django.db import models
from django.contrib.auth.models import User


from django.utils import timezone

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.fields.files import ImageFieldFile

from django.db.models import Max
from django.db import transaction

from django.db.models import Sum


from django.core.validators import MinValueValidator

from django.core.exceptions import ValidationError
import pandas as pd


class BaseModel(models.Model):
    last_saved = models.DateTimeField(default=timezone.now, blank=True, null=True)
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
        #print('\n\n\n>>>>>' , file_name)
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
        #print('>>>>>' , file_name)
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
                    #print('\n\ncompressed')
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


class UserExtra(BaseModel):
    ROLE_CHOICES = (
        ('admin', 'Quản Lý Cao Cấp'),
        ('technician', 'Kỹ Thuật'),
        ('supervisor', 'Giám Sát'),
        ('normal_staff', 'Nhân Viên'),
    )
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default="normal_staff")
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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



class ProjectUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=255, default="Member")
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)



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
        print(self.project.end_date)
        print(self.end_date)
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
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    plan_quantity = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    plan_amount = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    note = models.TextField(blank=True, null=True, default='')
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.plan_amount = self.plan_quantity * self.job.unit_price
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



class DataVehicleTypeDetail(BaseModel):
    VEHICLE_TYPE_CHOICES = (
        ('car', 'Xe con'),
        ('dump_truck', 'Xe ben'),
        ('excavator', 'Xe cuốc'),
        ('road_roller', 'Xe lu'),
        ('crane_truck', 'Xe cẩu'),
        ('bulldozer', 'Xe ủi'),
        ('loader', 'Xe xúc'),
    )

    # Vehicle Information Fields
    vehicle_type = models.CharField(max_length=255, verbose_name="Loại xe", choices=VEHICLE_TYPE_CHOICES)
    vehicle_type_detail = models.CharField(max_length=255, verbose_name="Loại xe chi tiết")

    # Revenue Information Fields
    revenue_per_8_hours = models.IntegerField(verbose_name="Đơn giá doanh thu", default=0, validators=[MinValueValidator(0)])
    # Resource Allocation Fields
    oil_consumption_per_hour = models.IntegerField(verbose_name="Định mức dầu 1 tiếng", default=0, validators=[MinValueValidator(0)])
    lubricant_consumption = models.IntegerField(verbose_name="Định mức nhớt", default=0, validators=[MinValueValidator(0)])
    insurance_fee = models.IntegerField(verbose_name="Định mức bảo hiểm", default=0, validators=[MinValueValidator(0)])
    road_fee_inspection = models.IntegerField(verbose_name="Định mức sử dụng đường bộ/Đăng kiểm", default=0, validators=[MinValueValidator(0)])
    tire_wear = models.IntegerField(verbose_name="Định mức hao mòn lốp xe", default=0, validators=[MinValueValidator(0)])
    police_fee = models.IntegerField(verbose_name="Định mức CA", default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f'{self.get_vehicle_type_display()} - {self.vehicle_type_detail}'

    @classmethod
    def get_display_fields(self):
        fields = ['vehicle_type', 'vehicle_type_detail', 'revenue_per_8_hours', 
                  'oil_consumption_per_hour', 'lubricant_consumption', 'insurance_fee', 
                  'road_fee_inspection', 'tire_wear', 'police_fee']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields
    # todo: thêm fields chạy ngày, chạy đêm, tabo ngày, mỗi cái có đơn giá => tính phí vận chuyể


class DataVehicle(BaseModel):
    vehicle_type = models.ForeignKey(DataVehicleTypeDetail, on_delete=models.CASCADE)
    license_plate = models.CharField(max_length=255, verbose_name="Biển kiểm soát", default="")
    vehicle_name = models.CharField(max_length=255, verbose_name="Tên nhận dạng xe", default="")
    gps_name = models.CharField(max_length=255, verbose_name="Tên trên định vị", default="")
    vehicle_inspection_number = models.CharField(max_length=255, verbose_name="Số đăng kiểm")
    vehicle_inspection_due_date = models.DateField(verbose_name="Thời hạn đăng kiểm", default=timezone.now)
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



class DataDriver(BaseModel):
    STATUS_CHOICES = (
        ('active', 'Đang làm việc'),
        ('on_leave', 'Nghỉ phép'),
        ('resigned', 'Đã thôi việc'),
        ('terminated', 'Bị sa thải'),
    )


    # Driver Information Fields
    full_name = models.CharField(max_length=255, verbose_name="Họ và tên")
    hire_date = models.DateField(verbose_name="Ngày vào làm", default=timezone.now)
    identity_card = models.CharField(max_length=255, verbose_name="CCCD", default="")
    birth_year = models.DateField(verbose_name="Ngày sinh", default=timezone.now)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="Trạng thái"
    )

    # Salary Fields
    basic_salary = models.PositiveIntegerField(verbose_name="Lương cơ bản", default=0)
    hourly_salary = models.PositiveIntegerField(verbose_name="Lương theo giờ", default=0)
    trip_salary = models.PositiveIntegerField(verbose_name="Lương theo chuyến", default=0)

    # Bank Information
    bank_name = models.CharField(max_length=255, verbose_name="Ngân hàng", default="")
    account_number = models.CharField(max_length=255, verbose_name="Số tài khoản", default="")
    account_holder_name = models.CharField(max_length=255, verbose_name="Tên chủ tài khoản", default="")

    # Other Information
    fixed_allowance = models.PositiveIntegerField(verbose_name="Phụ cấp cố định", default=0)
    insurance_amount = models.PositiveIntegerField(verbose_name="Số tiền tham gia BHXH", default=0)
    phone_number = models.CharField(max_length=15, verbose_name="Số điện thoại", default="")
    address = models.CharField(max_length=255, verbose_name="Địa chỉ", default="")
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f'{self.full_name}'

    @classmethod
    def get_display_fields(self):
        fields = ['full_name', 'hire_date', 'identity_card', 'birth_year', 'status', 
                  'basic_salary', 'hourly_salary', 'trip_salary',
                  'bank_name', 'account_number', 'account_holder_name',
                  'fixed_allowance', 'insurance_amount', 'phone_number', 'address']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

class DumbTruckPayRate(BaseModel):
    xe = models.ForeignKey(
        DataVehicle,
        on_delete=models.CASCADE,
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


