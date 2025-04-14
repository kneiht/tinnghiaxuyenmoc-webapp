from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator
from django.utils import timezone

from .base import models, BaseModel
from .project import Project
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class OperationReceiver(BaseModel):
    allow_display = True
    vietnamese_name = "Bên thụ hưởng chi phí vận hành"
    excel_downloadable = True
    excel_uploadable = True

    # Driver Information Fields
    name = models.CharField(
        max_length=255, verbose_name="Tên bên thụ hưởng", unique=True
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
        verbose_name="Tổng tiền đề xuất", default=0, validators=[MinValueValidator(0)]
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
        # Caculate payment states
        # Caculate total purchase amount
        purchase_amount = 0
        operation_orders = OperationOrder.objects.filter(operation_receiver=self)
        for operation_order in operation_orders:
            purchase_amount += operation_order.order_amount

        # Calculate total transferred amount
        transferred_amount = 0
        payment_records = OperationPaymentRecord.objects.filter(operation_receiver=self)
        for payment_record in payment_records:
            transferred_amount += payment_record.transferred_amount

        # Calculate total outstanding debt
        outstanding_debt = 0
        outstanding_debt = purchase_amount - transferred_amount
        # Update the fields
        self.total_purchase_amount = purchase_amount
        self.total_transferred_amount = transferred_amount
        self.total_outstanding_debt = outstanding_debt
        super().save(*args, **kwargs)


class OperationOrder(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Đề xuất thanh toán"

    APPROVAL_STATUS_CHOICES = (
        ("scratch", "Bảng nháp"),
        ("wait_for_approval", "Chờ duyệt"),
        ("approved", "Đã duyệt"),
        ("rejected", "Từ chối"),
    )

    PAID_STATUS_CHOICES = (
        ("paid", "Đã T.toán"),
        ("not_paid", "Chưa T.toán"),
        ("partial_paid", "T.toán một phần"),
    )
    PAYMENT_METHOD_CHOICES = (
        ("cash", "Tiền mặt"),
        ("personal_transfer", "Chuyển khoản cá nhân"),
        ("company_transfer", "Chuyển khoản công ty"),
    )

    class Meta:
        ordering = ["-created_at"]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Người trình",
    )
    order_code = models.CharField(
        max_length=255, verbose_name="Mã phiếu", default="", null=True, blank=True
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Dự án")

    order_amount = models.IntegerField(
        verbose_name="Tổng tiền đề xuất", default=0, validators=[MinValueValidator(0)]
    )

    approval_status = models.CharField(
        max_length=50,
        choices=APPROVAL_STATUS_CHOICES,
        default="scratch",
        verbose_name="Duyệt",
    )

    paid_status = models.CharField(
        max_length=50,
        choices=PAID_STATUS_CHOICES,
        default="not_paid",
        verbose_name="Thanh toán",
    )
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Hình thức thanh toán",
    )
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="Ngày tạo phiếu"
    )

    operation_receiver = models.ForeignKey(
        OperationReceiver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Bên thụ hưởng",
    )

    def __str__(self):
        return f"{self.order_code}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "order_code",
            "approval_status",
            "paid_status",
            "user",
            "operation_receiver",
            "order_amount",
            "payment_method",
            "note",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def __str__(self):
        return self.order_code

    def save(self, *args, **kwargs):
        # Skip if user changed (keep first user)
        if self.pk:
            old_instance = OperationOrder.objects.get(pk=self.pk)
            if old_instance.user:
                self.user = old_instance.user
        self.order_code = f"VH-{str(timezone.now().year)}-{str(self.pk).zfill(4)}"
        super().save()

        # Calculate total order amount => right in the field get from form

        # Check payment status
        payment_state = self.calculate_operation_receiver_state()
        total_purchase_amount = self.order_amount
        total_transferred_amount = payment_state["transferred_amount"]
        total_debt_amount = payment_state["debt_amount"]

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

        # Create or update payment record for this order
        if self.operation_receiver and self.approval_status == "approved":
            operation_receiver_state = self.calculate_operation_receiver_state()
            payment_records = OperationPaymentRecord.objects.filter(
                operation_order=self
            )

            if len(payment_records) == 0:
                payment_record = OperationPaymentRecord.objects.create(
                    operation_order=self,
                    operation_receiver=self.operation_receiver,
                    previous_debt=operation_receiver_state["debt_amount"],
                    purchase_amount=operation_receiver_state["purchase_amount"],
                )
            else:
                total_transferred_amount = 0
                previous_record = None
                purchase_amount = operation_receiver_state["purchase_amount"]

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
            OperationPaymentRecord.objects.filter(operation_order=self).delete()

    def calculate_operation_receiver_state(self):
        # Calculate total purchase amount
        purchase_amount = self.order_amount
        # Calculate total transferred amount
        transferred_amount = 0
        payment_records = OperationPaymentRecord.objects.filter(operation_order=self)
        for payment_record in payment_records:
            transferred_amount += payment_record.transferred_amount
        # Calculate total debt amount
        debt_amount = purchase_amount - transferred_amount

        state = {
            "purchase_amount": purchase_amount,
            "transferred_amount": transferred_amount,
            "debt_amount": debt_amount,
        }
        return state

    def delete(self, *args, **kwargs):
        operation_receiver = None
        operation_receiver = self.operation_receiver
        super().delete(*args, **kwargs)
        if operation_receiver:
            operation_receiver.save()


class OperationPaymentRecord(BaseModel):
    allow_display = True
    excel_downloadable = True
    vietnamese_name = "Thanh toán phiếu đề xuất"

    class Meta:
        ordering = ["operation_order", "operation_receiver", "-id"]

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
        verbose_name="Người tạo phiếu",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Dự án",
    )

    operation_order = models.ForeignKey(
        OperationOrder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Phiếu đề xuất",
    )
    operation_receiver = models.ForeignKey(
        OperationReceiver,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Bên thụ hưởng",
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
        upload_to="images/supply_payments/",
        blank=True,
        null=True,
    )
    image2 = models.ImageField(
        verbose_name="Hình ảnh",
        upload_to="images/supply_payments/",
        blank=True,
        null=True,
    )

    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Mã phiếu {self.operation_receiver} - Ngày tạo thanh toán {self.created_at}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "project",
            "operation_order",
            "operation_receiver",
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
        self.project = self.operation_order.project

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

        # Set user from supply order
        self.user = self.operation_order.user

        super().save(*args, **kwargs)
        self.operation_receiver.save()

        # Extract supply order and provider
        operation_order = self.operation_order
        operation_receiver = self.operation_receiver

        # Get last payment record for this supply order and provider
        last_payment_record = (
            OperationPaymentRecord.objects.filter(
                operation_order=operation_order,
                operation_receiver=operation_receiver,
            )
            .order_by("id")
            .last()
        )

        # Create new payment record if this is the last one, it's locked, and has remaining debt
        if last_payment_record == self and self.lock and self.debt != 0:
            new_payment_record = OperationPaymentRecord.objects.create(
                operation_order=operation_order,
                operation_receiver=operation_receiver,
                previous_debt=self.debt,
                purchase_amount=self.purchase_amount,
                debt=self.debt,
            )

        # Update supply order payment status
        operation_order.save(from_payment_record=True)

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


class OperationOrderImage(BaseModel):
    vietnamese_name = "Hình ảnh"
    order = models.ForeignKey(
        OperationOrder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Phiếu đề xuất",
    )
    image = models.ImageField(
        upload_to="project_operation/",
        verbose_name="Hình ảnh",
        default="",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Mã phiếu "{self.order}"'
