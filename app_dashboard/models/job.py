import pandas as pd

from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from .base import models, BaseModel, SecondaryIDMixin
from .project import Project




class Job(SecondaryIDMixin, BaseModel):
    allow_display = True
    vietnamese_name = "Công việc trong dự án"
    excel_downloadable = True
    excel_uploadable = True


    class Meta:
        verbose_name = "Công việc trong dự án"
    STATUS_CHOICES = (
        ('not_started', 'Chưa bắt đầu'),
        ('done', 'Hoàn thành'),
        ('in_progress', 'Đang thực hiện'),
        ('pending', 'Tạm hoãn'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="in_progress", verbose_name="Trạng thái")
    # price_code = models.CharField(max_length=255, default="", verbose_name="Mã hiệu đơn giá")
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

    def __str__(self):
        return f'{self.name} - {self.project.name}'

    def clean(self):
        errors = ""

        # Check if job has associated plans or reports and is being modified
        if not self._state.adding:  # Only check for existing jobs being modified
            original_job = Job.objects.get(pk=self.pk)
            has_plans = JobPlan.objects.filter(job=self).exists()
            has_reports = JobDateReport.objects.filter(job=self).exists()
            
            if (has_plans or has_reports) and (
                original_job.name != self.name or
                original_job.unit != self.unit or
                original_job.unit_price != self.unit_price or
                original_job.quantity != self.quantity or
                original_job.category != self.category
            ):
                errors += "- Không thể thay đổi thông tin công việc đã có kế hoạch tuần hoặc báo cáo ngày. \n- Ngoại trừ: Ghi chú, Ngày bắt đầu và Ngày kết thúc công việc.\n"

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





class JobPlan(BaseModel):
    
    allow_display = False # Đã luôn luôn cho phép trong view, False để không hiển thị trong permission
    vietnamese_name = "Kế hoạch tuần"
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
        return f'{self.job} từ {self.start_date} đến {self.end_date}'


class JobDateReport(BaseModel):
    allow_display = False # Đã luôn luôn cho phép trong view, False để không hiển thị trong permission
    vietnamese_name = "Báo cáo ngày"
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
        return f'{self.job} ngày {self.date}'

