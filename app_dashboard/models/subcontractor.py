from django.core.validators import MinValueValidator
from django.utils import timezone

from .base import models, BaseModel
from .project import Project

class Subcontractor(BaseModel):
    allow_display = True
    vietnamese_name = "Tổ đội/ Nhà thầu phụ"

    # Driver Information Fields
    name = models.CharField(max_length=255, verbose_name="Tổ đội/ nhà thầu phụ", unique=True)
    # Bank Information
    bank_name = models.CharField(max_length=255, verbose_name="Ngân hàng", default="", blank=True)
    account_number = models.CharField(max_length=255, verbose_name="Số tài khoản", default="", blank=True)
    account_holder_name = models.CharField(max_length=255, verbose_name="Tên chủ tài khoản", default="", blank=True)

    # Fianance
    total_purchase_amount = models.IntegerField(verbose_name="Tổng tiền thi công", default=0, validators=[MinValueValidator(0)])
    total_transferred_amount = models.IntegerField(verbose_name="Tổng thanh toán", default=0, validators=[MinValueValidator(0)])
    total_outstanding_debt = models.IntegerField(verbose_name="Tổng công nợ", default=0, validators=[MinValueValidator(0)])
    
    # Contact Information
    phone_number = models.CharField(max_length=15, verbose_name="Số điện thoại", default="")
    address = models.CharField(max_length=255, verbose_name="Địa chỉ", default="")
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
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



class BaseSubJob(BaseModel):
    allow_display = True
    vietnamese_name = "Công việc của tổ đội/ nhà thầu phụ"
    class Meta:
        ordering = ['job_number', 'job_name']
    job_type = models.CharField(max_length=50, default="Chưa phân loại", verbose_name="Nhóm công việc")
    job_number = models.CharField(max_length=255, verbose_name="Mã công việc", unique=True)
    job_name = models.CharField(max_length=255, verbose_name="Tên đầy đủ")
    unit = models.CharField(max_length=255, verbose_name="Đơn vị", default="chưa xác định", null=True, blank=True)
    image = models.ImageField(verbose_name="Hình ảnh", default="", null=True, blank=True)
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.job_number} - {self.job_name}'

    @classmethod
    def get_display_fields(self):
        fields = ['job_number', 'job_type', 'job_name', 'unit', 'image', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        DetailSubJob.objects.filter(base_sub_job=self).update(
            job_type=self.job_type,
            job_number=self.job_number,
            job_name=self.job_name,
            unit=self.unit,
            image=self.image
        )
        SubJobEstimation.objects.filter(base_sub_job=self).update(
            job_type=self.job_type,
            job_number=self.job_number,
            job_name=self.job_name,
            unit=self.unit
        )
    

 

class DetailSubJob(BaseModel):
    allow_display = True
    vietnamese_name = "Công việc chi tiết của tổ đội/ nhà thầu phụ"
    class Meta:
        ordering = ['subcontractor', 'job_type', 'job_number']
    subcontractor = models.ForeignKey(Subcontractor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tổ đội/ nhà thầu phụ")
    base_sub_job = models.ForeignKey(BaseSubJob, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Công việc")

    sub_job_price = models.IntegerField(verbose_name="Đơn giá", default=0, validators=[MinValueValidator(0)])

    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    valid_from = models.DateField(verbose_name="Ngày áp dụng", default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    # From BaseSubJob
    job_type = models.CharField(max_length=50, verbose_name="Nhóm công việc")
    job_number = models.CharField(max_length=255, verbose_name="Mã công việc", null=True, blank=True)
    job_name = models.CharField(max_length=255, verbose_name="Tên đầy đủ", null=True, blank=True)
    unit = models.CharField(max_length=255, verbose_name="Đơn vị", default="chưa xác định", null=True, blank=True)
    image = models.ImageField(verbose_name="Hình ảnh", default="", null=True, blank=True)
    # end From BaseSubJob


    def __str__(self):
        return f'{self.subcontractor} - {self.job_number} - {self.job_name}'

    @classmethod
    def get_display_fields(self):
        fields = ['subcontractor', 'job_number', 'job_type', 'job_name', 'sub_job_price', 'unit', 'image', 'note', 'valid_from']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields
    
    def save(self, *args, **kwargs):
        if self.base_sub_job:
            self.job_type = self.base_sub_job.job_type
            self.job_number = self.base_sub_job.job_number
            self.job_name = self.base_sub_job.job_name
            self.unit = self.base_sub_job.unit
            self.image = self.base_sub_job.image
        super().save()


class SubJobEstimation(BaseModel):
    allow_display = True
    vietnamese_name = "Dự toán công việc tổ đội/ nhà thầu phụ"
    class Meta:
        ordering = ['project', 'job_type', 'job_number']
        unique_together = ('project', 'base_sub_job')  # Enforces uniqueness

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Dự án")
    base_sub_job = models.ForeignKey(BaseSubJob, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Công việc")

    # From BaseSubJob
    job_type = models.CharField(max_length=50, verbose_name="Nhóm công việc")
    job_number = models.CharField(max_length=255, verbose_name="Mã công việc", null=True, blank=True)
    job_name = models.CharField(max_length=255, verbose_name="Tên đầy đủ", null=True, blank=True)
    unit = models.CharField(max_length=255, verbose_name="Đơn vị", default="chưa xác định", null=True, blank=True)
    # end From BaseSubJob

    quantity = models.FloatField(default=0.0, validators=[MinValueValidator(0)], verbose_name="Khối lượng")
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    @classmethod
    def get_display_fields(self):
        fields = ['job_type', 'job_number', 'job_name', 'unit', 'quantity', 'note']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields
    
    def save(self, *args, **kwargs):
        if self.base_sub_job:
            self.job_type = self.base_sub_job.job_type
            self.job_number = self.base_sub_job.job_number
            self.job_name = self.base_sub_job.job_name
            self.unit = self.base_sub_job.unit
        super().save()