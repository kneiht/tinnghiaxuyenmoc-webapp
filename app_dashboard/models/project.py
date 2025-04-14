from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


from .base import models, BaseModel
from .unclassified import Location


class Project(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Dự án"
    STATUS_CHOICES = (
        ("not_started", "Chưa bắt đầu"),
        ("done", "Hoàn thành"),
        ("in_progress", "Đang thực hiện"),
        ("pending", "Tạm hoãn"),
        ("archived", "Lưu trữ"),
    )

    name = models.CharField(
        max_length=2000, default="Dự án chưa được đặt tên", verbose_name="Tên dự án"
    )
    address = models.CharField(
        max_length=2000, verbose_name="Địa chỉ", default="Chưa thêm địa chỉ"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="in_progress",
        verbose_name="Trạng thái",
    )
    description = models.TextField(
        blank=True, null=True, default="", verbose_name="Mô tả"
    )
    image = models.ImageField(
        upload_to="images/projects/",
        blank=True,
        null=True,
        default="images/default/default_project.webp",
        verbose_name="Hình ảnh",
    )
    users = models.ManyToManyField(User, through="ProjectUser")
    start_date = models.DateField(default=timezone.now, verbose_name="Ngày bắt đầu")
    end_date = models.DateField(default=timezone.now, verbose_name="Ngày kết thúc")
    func_source = models.CharField(max_length=255, default="", verbose_name="Nguồn vốn")
    created_at = models.DateTimeField(default=timezone.now)
    location = models.OneToOneField(
        Location,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Địa điểm (dùng để cập nhật địa điểm)",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_number_of_jobs(self):
        return {
            "all": self.job_set.count(),
            "not_started": self.job_set.filter(status="not_started").count(),
            "done": self.job_set.filter(status="done").count(),
            "in_progress": self.job_set.filter(status="in_progress").count(),
            "pending": self.job_set.filter(status="pending").count(),
        }

    def save(self, *args, **kwargs):
        # Create a new location or update the existing one
        if not self.pk:
            # Create a new location
            location = Location.objects.create(
                name=self.name,
                address=self.address,
                type_of_location="du_an",
                note="Được tạo tự động từ Dự Án",
            )
            location.save()
            self.location = location
        else:
            # Update the existing location
            if self.location:
                self.location.name = self.name
                self.location.address = self.address
                self.location.type_of_location = "du_an"
                self.location.note = "Được tạo tự động từ Dự Án"
                self.location.save()

            else:
                # Create a new location
                location = Location.objects.create(
                    name=self.name,
                    address=self.address,
                    type_of_location="du_an",
                    note="Được tạo tự động từ Dự Án",
                )
                location.save()
                self.location = location
        # Save the project
        super().save(*args, **kwargs)


class ProjectUser(BaseModel):
    vietnamese_name = "Vị trí người dùng trong dự án"

    class Meta:
        unique_together = ("user", "project")

    ROLE_CHOICES = (
        ("view_only", "Chỉ xem"),
        ("technician", "Kỹ Thuật"),
        ("supervisor", "Giám Sát"),
        ("accountant", "Kế Toán"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Tài khoản")
    role = models.CharField(
        max_length=255, choices=ROLE_CHOICES, default="view_only", verbose_name="Vị trí"
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Dự án")
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.project.name} - {self.user.username} - {self.role}"

    @classmethod
    def get_display_fields(self):
        fields = ["user", "project", "role", "note"]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class ProjectPaymentRequest(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Đề xuất thanh toán"

    PAYMENT_METHOD_CHOICES = (
        ("cash", "Tiền mặt"),
        ("personal_transfer", "Chuyển khoản cá nhân"),
        ("company_transfer", "Chuyển khoản công ty"),
    )

    STATUS_CHOICES = (
        ("scratch", "Bảng nháp"),
        ("wait_for_approval", "Chờ duyệt"),
        ("approved", "Đã duyệt"),
        ("rejected", "Từ chối"),
        ("paid", "Đã thanh toán"),
    )

    request_number = models.CharField(
        max_length=50, verbose_name="Số đề nghị", unique=True
    )
    request_date = models.DateField(default=timezone.now, verbose_name="Ngày đề nghị")
    requester_name = models.CharField(max_length=255, verbose_name="Người đề nghị")
    department = models.CharField(max_length=255, verbose_name="Bộ phận")
    position = models.CharField(max_length=255, verbose_name="Chức vụ")
    amount = models.DecimalField(
        max_digits=15, decimal_places=0, verbose_name="Số tiền đề nghị"
    )
    note = models.TextField(verbose_name="Lý do thanh toán")
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name="Công trình",
        related_name="payment_requests",
    )
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Hình thức thanh toán",
    )
    recipient_name = models.CharField(max_length=255, verbose_name="Người nhận")

    # Bank information (for transfers)
    bank_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Ngân hàng"
    )
    account_number = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Số tài khoản"
    )
    account_holder = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Chủ tài khoản"
    )

    # Approval information
    approval_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Trạng thái",
    )

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Đề nghị thanh toán #{self.request_number} - {self.requester_name} - {self.amount}"

    class Meta:
        ordering = ["-request_date", "-created_at"]

    def clean(self):
        # Only allow changes to status if update
        if self.pk:
            original = ProjectPaymentRequest.objects.get(pk=self.pk)
            # iterate through all fields and check if they are changed
            for field in self._meta.fields:
                if field.name not in ["approval_status"]:
                    if getattr(self, field.name) != getattr(original, field.name):
                        raise ValidationError(
                            f"Chỉ có thể thay đổi trạng thái của đề nghị thanh toán sau khi tạo phiếu. \n Vui lòng xóa và tạo lại phiếu khác nếu cần thay đổi thông tin."
                        )

        # Validate that bank information is provided for bank transfers
        if self.payment_method in ["personal_transfer", "company_transfer"]:
            if not self.bank_name or not self.account_number or not self.account_holder:
                raise ValidationError(
                    "Thông tin ngân hàng là bắt buộc cho hình thức chuyển khoản"
                )

    @classmethod
    def get_display_fields(self):
        return [
            "project",
            "request_number",
            "request_date",
            "approval_status",
            "requester_name",
            "amount",
            "payment_method",
            "recipient_name",
        ]
