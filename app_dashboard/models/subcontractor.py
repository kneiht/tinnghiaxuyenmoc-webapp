from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator
from django.utils import timezone

from .base import models, BaseModel
from .project import Project
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class SubContractor(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Tổ đội/ Nhà thầu phụ"

    # Driver Information Fields
    name = models.CharField(
        max_length=255, verbose_name="Tổ đội/ nhà thầu phụ", unique=True
    )
    # Bank Information
    bank_name = models.CharField(
        max_length=255, verbose_name="Ngân hàng", default="", blank=True
    )
    account_number = models.CharField(
        max_length=255, verbose_name="Số tài khoản", default="", blank=True
    )
    account_holder_name = models.CharField(
        max_length=255, verbose_name="Tên chủ tài khoản", default="", blank=True
    )

    # Fianance
    total_purchase_amount = models.IntegerField(
        verbose_name="Tổng tiền thi công", default=0, validators=[MinValueValidator(0)]
    )
    total_transferred_amount = models.IntegerField(
        verbose_name="Tổng thanh toán", default=0, validators=[MinValueValidator(0)]
    )
    total_outstanding_debt = models.IntegerField(
        verbose_name="Tổng công nợ", default=0, validators=[MinValueValidator(0)]
    )

    # Contact Information
    phone_number = models.CharField(
        max_length=15, verbose_name="Số điện thoại", default=""
    )
    address = models.CharField(max_length=255, verbose_name="Địa chỉ", default="")
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.phone_number}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "name",
            "phone_number",
            "address",
            "bank_name",
            "account_number",
            "account_holder_name",
            "total_purchase_amount",
            "total_transferred_amount",
            "total_outstanding_debt",
            "note",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # calculate_payment_states
        # Get all SubJobOrderSubJob records for this provider
        order_sub_jobs = SubJobOrderSubJob.objects.filter(
            detail_sub_job__sub_contractor=self
        )

        # Calculate total purchase amount
        purchase_amount = 0
        for order_sub_job in order_sub_jobs:
            if order_sub_job:
                purchase_amount += order_sub_job.sub_job_price * order_sub_job.quantity

        # Calculate total transferred amount from payment records
        transferred_amount = 0
        payment_records = SubJobPaymentRecord.objects.filter(sub_contractor=self)
        for payment_record in payment_records:
            transferred_amount += payment_record.transferred_amount

        # Calculate outstanding debt
        debt_amount = purchase_amount - transferred_amount

        # Update provider's financial fields
        self.total_purchase_amount = purchase_amount
        self.total_transferred_amount = transferred_amount
        self.total_outstanding_debt = debt_amount
        super().save(*args, **kwargs)


class SubJobBrand(BaseModel):
    allow_display = True
    excel_downloadable = True
    vietnamese_name = "Thương hiệu công việc"
    name = models.CharField(max_length=255, verbose_name="Tên thương hiệu", unique=True)
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    @classmethod
    def get_display_fields(self):
        fields = [
            "name",
            "note",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class BaseSubJob(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Công việc của tổ đội/ nhà thầu phụ"

    JOB_TYPE_CHOICES = (
        ("Hạ tầng kỹ thuật", "Hạ tầng kỹ thuật"),
        ("Giao thông", "Giao thông"),
        ("Dân dụng và công nghiệp", "Dân dụng và công nghiệp"),
        ("Thủy lợi", "Thủy lợi"),
        ("Điện trung hạ thế", "Điện trung hạ thế"),
        ("Điện chiếu sáng", "Điện chiếu sáng"),
    )

    class Meta:
        ordering = ["job_number", "job_name"]

    job_type = models.CharField(
        max_length=50,
        choices=JOB_TYPE_CHOICES,
        default="Chưa phân loại",
        verbose_name="Nhóm công việc",
    )
    job_number = models.CharField(
        max_length=255, verbose_name="Mã công việc", unique=True
    )
    job_name = models.CharField(max_length=2000, verbose_name="Tên đầy đủ")
    unit = models.CharField(
        max_length=255,
        verbose_name="Đơn vị",
        default="chưa xác định",
        null=True,
        blank=True,
    )
    image = models.ImageField(
        verbose_name="Hình ảnh", default="", null=True, blank=True
    )
    reference = models.CharField(
        max_length=2000,
        verbose_name="Công trình tham khảo",
        default="",
        null=True,
        blank=True,
    )
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.job_number} - {self.job_name}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "job_number",
            "job_type",
            "job_name",
            "unit",
            "image",
            "reference",
            "note",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def save(self, *args, **kwargs):
        # First created, lock
        if self._state.adding:
            self.lock = True
        super().save(*args, **kwargs)
        DetailSubJob.objects.filter(base_sub_job=self).update(
            job_type=self.job_type,
            job_number=self.job_number,
            job_name=self.job_name,
            unit=self.unit,
            image=self.image,
        )
        SubJobEstimation.objects.filter(base_sub_job=self).update(
            job_type=self.job_type,
            job_number=self.job_number,
            job_name=self.job_name,
            unit=self.unit,
        )

    def get_sub_contractors(self):
        """Get list of sub contracts that have this base sub job"""
        detail_sub_jobs = DetailSubJob.objects.filter(base_sub_job=self)
        sub_contractors = []
        sub_contractor_ids = [job.sub_contractor.id for job in detail_sub_jobs]
        sub_contractor_ids = set(sub_contractor_ids)
        for sub_contractor in sub_contractor_ids:
            sub_contractor = SubContractor.objects.get(pk=sub_contractor)
            sub_contractors.append(sub_contractor)
        return sub_contractors

    def get_list_of_detail_sub_jobs_of_a_sub_contractor(self, sub_contractor):
        """Get list of detail sub jobs that have this base sub job"""
        detail_sub_jobs = DetailSubJob.objects.filter(
            base_sub_job=self, sub_contractor=sub_contractor
        ).order_by("-valid_from")
        return detail_sub_jobs

    def get_history(self, sub_contractor):
        """Get list of sub job order sub jobs that have this base sub job"""
        sub_job_order_sub_jobs = SubJobOrderSubJob.objects.filter(
            base_sub_job=self, detail_sub_job__sub_contractor=sub_contractor
        ).order_by("-created_at")

        return [
            {
                "price": sub_job_order_sub_job.sub_job_price,
                "create_at": sub_job_order_sub_job.created_at,
                "project": sub_job_order_sub_job.sub_job_order.project,
            }
            for sub_job_order_sub_job in sub_job_order_sub_jobs
        ]

    def get_dict_of_detail_sub_jobs(self):
        sub_contractors = self.get_sub_contractors()
        detail_sub_job_dict = {}
        for sub_contractor in sub_contractors:
            detail_sub_jobs = self.get_list_of_detail_sub_jobs_of_a_sub_contractor(
                sub_contractor
            )
            sub_contractor.history = self.get_history(sub_contractor)
            detail_sub_job_dict[sub_contractor] = detail_sub_jobs

        return detail_sub_job_dict


class DetailSubJob(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Công việc chi tiết của tổ đội/ nhà thầu phụ"

    class Meta:
        ordering = ["sub_contractor", "job_type", "job_number"]

    sub_contractor = models.ForeignKey(
        SubContractor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tổ đội/ nhà thầu phụ",
    )

    base_sub_job = models.ForeignKey(
        BaseSubJob,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Công việc",
    )

    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    valid_from = models.DateField(verbose_name="Ngày áp dụng", default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    # From BaseSubJob
    job_type = models.CharField(max_length=50, verbose_name="Nhóm công việc")
    job_number = models.CharField(
        max_length=255, verbose_name="Mã công việc", null=True, blank=True
    )
    job_name = models.CharField(
        max_length=2000, verbose_name="Tên đầy đủ", null=True, blank=True
    )
    unit = models.CharField(
        max_length=255,
        verbose_name="Đơn vị",
        default="chưa xác định",
        null=True,
        blank=True,
    )
    image = models.ImageField(
        verbose_name="Hình ảnh", default="", null=True, blank=True
    )
    # end From BaseSubJob

    image_prove = models.FileField(
        verbose_name="Hình ảnh chứng minh",
        default="",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "pdf"])
        ],
    )

    def __str__(self):
        return f"{self.sub_contractor.name} - {self.job_number} - {self.job_name}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "sub_contractor",
            "job_number",
            "job_type",
            "job_name",
            "unit",
            "image",
            "image_prove",
            "note",
            "valid_from",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def save(self, *args, **kwargs):
        # First created, lock
        if self._state.adding:
            self.lock = True
        if self.base_sub_job:
            self.job_type = self.base_sub_job.job_type
            self.job_number = self.base_sub_job.job_number
            self.job_name = self.base_sub_job.job_name
            self.unit = self.base_sub_job.unit
            self.image = self.base_sub_job.image
        super().save()


class SubJobEstimation(BaseModel):
    allow_display = True
    excel_downloadable = True
    vietnamese_name = "Dự toán công việc tổ đội/ nhà thầu phụ"

    class Meta:
        ordering = ["project", "job_type", "job_number"]
        unique_together = ("project", "base_sub_job")  # Enforces uniqueness

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Dự án")

    base_sub_job = models.ForeignKey(
        BaseSubJob,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Công việc",
    )

    # From BaseSubJob
    job_type = models.CharField(max_length=50, verbose_name="Nhóm công việc")
    job_number = models.CharField(
        max_length=255, verbose_name="Mã công việc", null=True, blank=True
    )
    job_name = models.CharField(
        max_length=2000, verbose_name="Tên đầy đủ", null=True, blank=True
    )
    unit = models.CharField(
        max_length=255,
        verbose_name="Đơn vị",
        default="chưa xác định",
        null=True,
        blank=True,
    )
    # end From BaseSubJob

    quantity = models.FloatField(
        default=0.0, validators=[MinValueValidator(0)], verbose_name="Khối lượng"
    )
    orderable_quantity = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0)],
        verbose_name="Khối lượng còn thiếu",
    )
    ordered_quantity = models.FloatField(
        default=0.0, validators=[MinValueValidator(0)], verbose_name="Khối lượng đã đặt"
    )
    paid_quantity = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0)],
        verbose_name="Khối lượng đã thanh toán",
    )
    received_quantity = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0)],
        verbose_name="Khối lượng đã hoàn thành",
    )

    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return (
            f"Dự án {self.project.name} - Công việc {self.job_number} - {self.job_name}"
        )

    @classmethod
    def get_display_fields(self):
        fields = [
            "job_type",
            "job_number",
            "job_name",
            "unit",
            "quantity",
            "orderable_quantity",
            "ordered_quantity",
            "paid_quantity",
            "received_quantity",
            "note",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def save(self, *args, **kwargs):
        if self.note == "nan":
            self.note = ""
        if self.base_sub_job:
            self.job_type = self.base_sub_job.job_type
            self.job_number = self.base_sub_job.job_number
            self.job_name = self.base_sub_job.job_name
            self.unit = self.base_sub_job.unit
        self.orderable_quantity = self.get_orderable_quantity()
        self.ordered_quantity = self.get_ordered_quantity()
        self.paid_quantity = self.get_paid_quantity()
        self.received_quantity = self.get_received_quantity()
        super().save()

    # estimate_quantity
    def get_estimate_quantity(self):
        return self.quantity

    # orderable_quantity
    def get_orderable_quantity(self):
        # Gell all sub job order sub jobs for this project and base_sub_job
        sub_job_orders = SubJobOrderSubJob.objects.filter(
            sub_job_order__project=self.project, base_sub_job=self.base_sub_job
        )
        # Calculate total ordered quantity
        total_ordered = sum(order.quantity for order in sub_job_orders)
        # Maximum orderable quantity is the difference between estimated and ordered
        max_orderable = self.quantity - total_ordered
        return max_orderable

    # ordered_quantity
    def get_ordered_quantity(self):
        # Gell all sub job order sub jobs for this project and base_sub_job
        sub_job_orders = SubJobOrderSubJob.objects.filter(
            sub_job_order__project=self.project, base_sub_job=self.base_sub_job
        )
        # Calculate total ordered quantity
        total_ordered = sum(order.quantity for order in sub_job_orders)
        return total_ordered

    # paid_quantity
    def get_paid_quantity(self):
        # Gell all sub job order sub jobs for this project and base_sub_job
        sub_job_orders = SubJobOrderSubJob.objects.filter(
            sub_job_order__project=self.project, base_sub_job=self.base_sub_job
        )
        total_paid = sum(order.paid_quantity for order in sub_job_orders)
        return total_paid

    # received_quantity
    def get_received_quantity(self):
        # Gell all sub job order sub jobs for this project and base_sub_job
        sub_job_orders = SubJobOrderSubJob.objects.filter(
            sub_job_order__project=self.project, base_sub_job=self.base_sub_job
        )
        total_received = sum(order.received_quantity for order in sub_job_orders)
        return total_received


class SubJobOrder(BaseModel):
    allow_display = True
    excel_downloadable = True
    vietnamese_name = "Đặt công việc"

    APPROVAL_STATUS_CHOICES = (
        ("scratch", "Bảng nháp"),
        ("wait_for_approval", "Chờ duyệt"),
        ("approved", "Đã duyệt"),
        ("rejected", "Từ chối"),
    )

    RECEIVED_STATUS_CHOICES = (
        ("received", "Đã H.Thành"),
        ("not_received", "Chưa H.Thành"),
        ("partial_received", "H.Thành một phần"),
    )

    PAID_STATUS_CHOICES = (
        ("paid", "Đã T.toán"),
        ("not_paid", "Chưa T.toán"),
        ("partial_paid", "T.toán một phần"),
    )

    class Meta:
        ordering = ["-created_at"]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người tạo"
    )
    order_code = models.CharField(
        max_length=255, verbose_name="Mã phiếu", default="", null=True, blank=True
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Dự án")

    order_amount = models.IntegerField(
        verbose_name="Tổng tiền", default=0, validators=[MinValueValidator(0)]
    )

    approval_status = models.CharField(
        max_length=50,
        choices=APPROVAL_STATUS_CHOICES,
        default="scratch",
        verbose_name="Duyệt",
    )
    received_status = models.CharField(
        max_length=50,
        choices=RECEIVED_STATUS_CHOICES,
        default="not_received",
        verbose_name="Hoàn thành",
    )
    paid_status = models.CharField(
        max_length=50,
        choices=PAID_STATUS_CHOICES,
        default="not_paid",
        verbose_name="Thanh toán",
    )

    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="Ngày tạo phiếu"
    )
    sub_contractors = models.TextField(
        verbose_name="Các tổ đội/ nhà thầu phụ", default="", null=True, blank=True
    )

    def __str__(self):
        return f"{self.order_code}"

    def save(self, *args, **kwargs):
        # Skip if user changed (keep first user)
        if self.pk:
            old_instance = SubJobOrder.objects.get(pk=self.pk)
            if old_instance.user:
                self.user = old_instance.user
        self.order_code = "#" + str(self.pk).zfill(4)
        super().save()

        # Get all related subjob orders
        order_sub_jobs = SubJobOrderSubJob.objects.filter(sub_job_order=self)

        # Calculate total order amount
        total_amount = 0
        for order_sub_job in order_sub_jobs:
            if order_sub_job:
                subjob_amount = order_sub_job.sub_job_price * order_sub_job.quantity
                total_amount += subjob_amount

        self.order_amount = total_amount

        # Check received status
        if (
            order_sub_jobs.count() > 0
            and order_sub_jobs.count
            == order_sub_jobs.filter(received_status="received").count()
        ):
            self.received_status = "received"
        elif (
            order_sub_jobs.count() > 0
            and order_sub_jobs.filter(received_status="partial_received").count() > 0
        ):
            self.received_status = "partial_received"
        else:
            self.received_status = "not_received"

        # Check payment status and update providers list
        all_provider_payment_states = self.calculate_all_provider_payment_states()
        total_purchase_amount = 0
        total_transferred_amount = 0
        total_debt_amount = 0
        self.sub_contractors = ""

        for provider_id, provider_payment_state in all_provider_payment_states.items():
            total_purchase_amount += provider_payment_state["purchase_amount"]
            total_transferred_amount += provider_payment_state["transferred_amount"]
            total_debt_amount += provider_payment_state["debt_amount"]

            provider = SubContractor.objects.get(pk=provider_id)
            self.sub_contractors += "- " + provider.name + "\n"
        self.sub_contractors = self.sub_contractors.strip()

        # Update paid status
        if total_purchase_amount == 0:
            self.paid_status = "not_paid"
        else:
            if total_debt_amount == 0:
                self.paid_status = "paid"
            elif total_debt_amount > 0 and total_transferred_amount > 0:
                self.paid_status = "partial_paid"
            else:
                self.paid_status = "not_paid"
        super().save()

        # Prevent recursion from payment records
        from_payment_record = kwargs.get("from_payment_record", None)
        if from_payment_record:
            return

        # Create or update payment records
        if self.approval_status == "approved":
            all_provider_payment_state = self.calculate_all_provider_payment_states()

            for provider_id in all_provider_payment_state:
                payment_records = SubJobPaymentRecord.objects.filter(
                    sub_job_order=self, sub_contractor=provider_id
                ).order_by("id")

                if len(payment_records) == 0:
                    payment_record = SubJobPaymentRecord.objects.create(
                        sub_job_order=self,
                        sub_contractor_id=provider_id,
                        previous_debt=all_provider_payment_state[provider_id][
                            "debt_amount"
                        ],
                        purchase_amount=all_provider_payment_state[provider_id][
                            "purchase_amount"
                        ],
                    )
                else:
                    total_transferred_amount = 0
                    previous_record = None
                    purchase_amount = all_provider_payment_state[provider_id][
                        "purchase_amount"
                    ]

                    for payment_record in payment_records:
                        total_transferred_amount += (
                            previous_record.transferred_amount if previous_record else 0
                        )
                        previous_record = payment_record
                        previous_debt = purchase_amount - total_transferred_amount
                        payment_record.previous_debt = previous_debt
                        payment_record.purchase_amount = purchase_amount
                        payment_record.debt = (
                            previous_debt - payment_record.transferred_amount
                        )
                        payment_record.save()

        elif self.approval_status == "rejected":
            SubJobPaymentRecord.objects.filter(sub_job_order=self).delete()

    @classmethod
    def get_display_fields(self):
        fields = [
            "order_code",
            "approval_status",
            "received_status",
            "paid_status",
            "note",
            "created_at",
            "user",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def __str__(self):
        return self.order_code

    def calculate_all_provider_payment_states(self):
        # Get all sub jobs in this sub job order
        order_sub_jobs = SubJobOrderSubJob.objects.filter(sub_job_order=self)

        # Get all providers in this sub job order
        provider_ids = order_sub_jobs.values_list(
            "detail_sub_job__sub_contractor", flat=True
        ).distinct()
        provider_ids = set(provider_ids)

        all_provider_payment_state = {}
        for provider_id in provider_ids:
            if not provider_id:  # Skip if provider is None
                continue

            provider = SubContractor.objects.get(pk=provider_id)

            # Calculate purchase amount
            purchase_amount = 0
            provider_sub_jobs = order_sub_jobs.filter(
                detail_sub_job__sub_contractor=provider
            )
            for sub_job in provider_sub_jobs:
                if sub_job:
                    purchase_amount += sub_job.sub_job_price * sub_job.quantity

            # Calculate transferred amount
            transferred_amount = 0
            payment_records = SubJobPaymentRecord.objects.filter(
                sub_job_order=self, sub_contractor=provider
            )
            for payment_record in payment_records:
                transferred_amount += payment_record.transferred_amount

            # Calculate debt amount
            debt_amount = purchase_amount - transferred_amount

            state = {
                "purchase_amount": purchase_amount,
                "transferred_amount": transferred_amount,
                "debt_amount": debt_amount,
            }
            all_provider_payment_state[provider.id] = state

        return all_provider_payment_state

    def get_sub_job_order_base_sub_job_list(self):
        order_sub_jobs = SubJobOrderSubJob.objects.filter(
            sub_job_order=self, base_sub_job__isnull=False
        )
        return order_sub_jobs

    def get_sub_job_order_detail_sub_job_list(self):
        order_sub_jobs = SubJobOrderSubJob.objects.filter(
            sub_job_order=self, detail_sub_job__isnull=False
        )
        # Put into dict of groups of providers
        sub_job_order_sub_job_dict = {}
        for order_sub_job in order_sub_jobs:
            if (
                order_sub_job.detail_sub_job.sub_contractor
                not in sub_job_order_sub_job_dict
            ):
                sub_job_order_sub_job_dict[
                    order_sub_job.detail_sub_job.sub_contractor
                ] = []
            sub_job_order_sub_job_dict[
                order_sub_job.detail_sub_job.sub_contractor
            ].append(order_sub_job)
        return sub_job_order_sub_job_dict


class SubJobOrderSubJob(BaseModel):
    vietnamese_name = "Công việc trong đơn đặt nhân công"
    RECEIVED_STATUS_CHOICES = (
        ("received", "Đã H.Thành"),
        ("not_received", "Chưa H.Thành"),
        ("partial_received", "H.Thành một phần"),
    )

    sub_job_order = models.ForeignKey(
        SubJobOrder, on_delete=models.CASCADE, verbose_name="Đơn hàng"
    )

    base_sub_job = models.ForeignKey(
        BaseSubJob,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Công việc",
    )
    detail_sub_job = models.ForeignKey(
        DetailSubJob,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Công việc chi tiết",
    )

    sub_job_price = models.IntegerField(
        verbose_name="Đơn giá", default=0, validators=[MinValueValidator(0)]
    )

    quantity = models.IntegerField(
        verbose_name="Số lượng", default=0, validators=[MinValueValidator(0)]
    )
    paid_quantity = models.IntegerField(
        verbose_name="Số lượng đã T.toán",
        default=0,
        validators=[MinValueValidator(0)],
    )
    received_quantity = models.IntegerField(
        verbose_name="Số lượng đã H.Thành", default=0, validators=[MinValueValidator(0)]
    )
    received_status = models.CharField(
        max_length=50,
        choices=RECEIVED_STATUS_CHOICES,
        default="not_received",
        verbose_name="Trạng thái hoàn thành",
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.sub_job_order.order_code} - {self.base_sub_job}"

    def delete(self, *args, **kwargs):
        provider = None
        if self.detail_sub_job:
            provider = self.detail_sub_job.sub_contractor
        super().delete(*args, **kwargs)
        if provider:
            provider.save()

    def save(self, *args, **kwargs):
        # Get old provider before saving
        old_provider = None
        if self.pk:
            old_instance = SubJobOrderSubJob.objects.get(pk=self.pk)
            if old_instance.detail_sub_job:
                old_provider = old_instance.detail_sub_job.sub_contractor

        # Get new provider after saving
        new_provider = None
        if self.detail_sub_job:
            new_provider = self.detail_sub_job.sub_contractor

        # Update payment states for both old and new providers
        if old_provider and old_provider != new_provider:
            old_provider.save()
        if new_provider:
            new_provider.save()

        # update cost estimation
        cost_estimation = SubJobEstimation.objects.filter(
            project=self.sub_job_order.project, base_sub_job=self.base_sub_job
        ).first()
        cost_estimation.save()

        if self.quantity:
            if self.received_quantity == self.quantity:
                self.received_status = "received"
            elif self.received_quantity > 0 and self.received_quantity < self.quantity:
                self.received_status = "partial_received"
            else:
                self.received_status = "not_received"
        else:
            self.received_status = "not_received"

        super().save(*args, **kwargs)

    # estimate_quantity
    def estimate_quantity(self):
        cost_estimation = SubJobEstimation.objects.filter(
            project=self.sub_job_order.project, base_sub_job=self.base_sub_job
        ).first()
        if cost_estimation:
            return cost_estimation.quantity
        else:
            return 0.0

    def orderable_quantity(self):
        # Get cost estimation for this project and supply
        cost_estimation = SubJobEstimation.objects.filter(
            project=self.sub_job_order.project, base_sub_job=self.base_sub_job
        ).first()
        orderable_quantity = cost_estimation.get_orderable_quantity() + self.quantity
        return orderable_quantity


class SubJobPaymentRecord(BaseModel):
    allow_display = True
    excel_downloadable = True
    vietnamese_name = "Thanh toán công việc"

    class Meta:
        ordering = ["sub_job_order", "sub_contractor", "-id"]

    PAID_STATUS_CHOICES = (
        ("not_requested", "Chưa đề nghị"),
        ("requested", "Đề nghị T.toán"),
        ("partial_paid", "T.toán một phần"),
        ("paid", "Đã T.toán đủ"),
    )

    MONEY_SOURCE_CHOICES = (
        ("individual", "Cá nhân"),
        ("huy_bao_company", "Công ty Huy Bảo"),
        ("tin_nghia_company", "Công ty Tín Nghĩa"),
        ("viet_tin_company", "Công ty Việt Tín"),
        ("dhc_company", "Công ty DHC"),
        ("bh_company", "Công ty BH"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Người tạo",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Dự án",
    )
    sub_job_order = models.ForeignKey(
        SubJobOrder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Phiếu đặt công việc",
    )
    sub_contractor = models.ForeignKey(
        SubContractor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Tổ đội/ nhà thầu phụ",
    )
    status = models.CharField(
        max_length=50,
        choices=PAID_STATUS_CHOICES,
        default="not_requested",
        verbose_name="Trạng thái thanh toán",
    )
    purchase_amount = models.IntegerField(
        verbose_name="Tổng tiền trên phiếu",
        default=0,
        validators=[MinValueValidator(0)],
    )
    previous_debt = models.IntegerField(
        verbose_name="Nợ kì trước", default=0, validators=[MinValueValidator(0)]
    )
    requested_amount = models.IntegerField(
        verbose_name="Số tiền đề nghị", default=0, validators=[MinValueValidator(0)]
    )
    requested_date = models.DateField(verbose_name="Ngày đề nghị", default=timezone.now)
    money_source = models.CharField(
        max_length=100,
        choices=MONEY_SOURCE_CHOICES,
        default="individual",
        verbose_name="Nguồn tiền",
    )
    transferred_amount = models.IntegerField(
        verbose_name="Tiền thanh toán", default=0, validators=[MinValueValidator(0)]
    )
    payment_date = models.DateField(
        verbose_name="Ngày thanh toán", default=timezone.now
    )
    debt = models.IntegerField(
        verbose_name="Nợ còn lại", default=0, validators=[MinValueValidator(0)]
    )
    lock = models.BooleanField(verbose_name="Khóa phiếu", default=False)
    image1 = models.ImageField(
        verbose_name="Hình ảnh",
        upload_to="images/sub_job_payments/",
        blank=True,
        null=True,
    )
    image2 = models.ImageField(
        verbose_name="Hình ảnh",
        upload_to="images/sub_job_payments/",
        blank=True,
        null=True,
    )
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Mã phiếu {self.sub_job_order} - Ngày tạo thanh toán {self.created_at}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "project",
            "sub_job_order",
            "sub_contractor",
            "status",
            "lock",
            "purchase_amount",
            "previous_debt",
            "requested_amount",
            "requested_date",
            "transferred_amount",
            "payment_date",
            "money_source",
            "debt",
            "note",
            "image1",
            "user",
        ]
        return [field for field in fields if hasattr(self, field)]

    def save(self, *args, **kwargs):
        self.project = self.sub_job_order.project
        # Update status based on amounts
        if self.requested_amount > 0:
            self.status = "requested"

        if self.transferred_amount > 0 and self.transferred_amount < self.previous_debt:
            self.status = "partial_paid"
            self.debt = self.previous_debt - self.transferred_amount

        if (
            self.transferred_amount > 0
            and self.transferred_amount == self.previous_debt
        ):
            self.status = "paid"
            self.debt = self.previous_debt - self.transferred_amount

        if self.requested_amount == 0:
            self.status = "not_requested"

        # Set user from sub job order
        self.user = self.sub_job_order.user

        super().save(*args, **kwargs)
        self.sub_contractor.save()

        # Extract sub job order and sub contractor
        sub_job_order = self.sub_job_order
        sub_contractor = self.sub_contractor

        # Get last payment record for this sub job order and sub contractor
        last_payment_record = (
            SubJobPaymentRecord.objects.filter(
                sub_job_order=sub_job_order, sub_contractor=sub_contractor
            )
            .order_by("id")
            .last()
        )

        # Create new payment record if this is the last one, it's locked, and has remaining debt
        if last_payment_record == self and self.lock and self.debt != 0:
            new_payment_record = SubJobPaymentRecord.objects.create(
                sub_job_order=sub_job_order,
                sub_contractor=sub_contractor,
                previous_debt=self.debt,
                purchase_amount=self.purchase_amount,
                debt=self.debt,
            )

        # Update sub job order payment status
        sub_job_order.save(from_payment_record=True)

    def clean(self):
        errors = ""
        if self.requested_amount > self.previous_debt:
            errors += f'- Số tiền đề nghị phải nhỏ hơn hoặc bằng nợ kì trước {format(self.previous_debt, ",d")}.\n'

        if self.requested_amount == 0 and self.transferred_amount > 0:
            errors += "- Chưa thanh toán khi chưa có đề nghị.\n"

        if self.transferred_amount > self.previous_debt:
            errors += f'- Số tiền thanh toán phải nhỏ hơn hoặc bằng nợ kì trước {format(self.previous_debt, ",d")}.\n'

        if self.payment_date < self.requested_date:
            errors += f'- Ngày thanh toán phải lớn hơn hoặc bằng ngày đề nghị {self.requested_date.strftime("%d/%m/%Y")}.\n'

        if self.lock and self.transferred_amount == 0:
            errors += "- Không thể khóa phiếu thanh toán khi chưa thanh toán.\n"

        if errors:
            raise ValidationError(errors)


class SubJobOrderImage(BaseModel):
    vietnamese_name = "Hình ảnh"
    order = models.ForeignKey(
        SubJobOrder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Phiếu đặt công việc",
    )
    image = models.ImageField(
        upload_to="project_subjob_images/",
        verbose_name="Hình ảnh",
        default="",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Mã phiếu "{self.order}"'
