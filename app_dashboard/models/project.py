
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


from .base import models, BaseModel

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
    class Meta:
        unique_together = ('user', 'project')

    ROLE_CHOICES = (
        ('view_only', 'Chỉ xem'),
        ('technician', 'Kỹ Thuật'),
        ('supervisor', 'Giám Sát'),
        ('accountant', 'Kế Toán'),
        ('all', 'Cấp tất cả quyền trong dự án'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Tài khoản")
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
