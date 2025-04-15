from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from app_dashboard.models.unclassified import VehicleDetail, VehicleType
from app_dashboard.models.base import models, BaseModel
from django.core.exceptions import ValidationError


class VehicleMaintenance(BaseModel):

    allow_display = True
    excel_downloadable = True
    vietnamese_name = "Sửa Chữa"

    MAINTENANCE_CATEGORY_CHOICES = (
        ("periodic_check", "Bảo dưỡng/ Sửa chữa nhỏ/ Kiểm tra định kì"),
        ("repair", "Sửa chữa lớn/ sửa chữa hư hỏng"),
    )
    APPROVAL_STATUS_CHOICES = (
        ("scratch", "Bảng nháp"),
        ("wait_for_approval", "Chờ duyệt"),
        ("approved", "Đã duyệt"),
        ("rejected", "Từ chối"),
    )
    RECEIVED_STATUS_CHOICES = (
        ("received", "Đã nhận"),
        ("not_received", "Chưa nhận"),
    )
    PAID_STATUS_CHOICES = (
        ("paid", "Đã T.toán"),
        ("not_paid", "Chưa T.toán"),
        ("partial_paid", "T.toán một phần"),
    )
    DONE_STATUS_CHOICES = (
        ("done", "Xong"),
        ("not_done", "Chưa xong"),
    )

    class Meta:
        ordering = ["-created_at"]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Người tạo phiếu",
    )
    repair_code = models.CharField(
        max_length=255, verbose_name="Mã phiếu", default="", null=True, blank=True
    )
    vehicle = models.ForeignKey(
        VehicleDetail,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Xe",
    )
    maintenance_amount = models.IntegerField(
        verbose_name="Chi phí", default=0, validators=[MinValueValidator(0)]
    )
    maintenance_category = models.CharField(
        max_length=255,
        choices=MAINTENANCE_CATEGORY_CHOICES,
        verbose_name="Phân loại",
        default="",
        null=True,
        blank=True,
    )
    from_date = models.DateField(verbose_name="Ngày nhận", default=timezone.now)
    to_date = models.DateField(verbose_name="Ngày xong", default=timezone.now)

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
        verbose_name="Nhận hàng",
    )
    paid_status = models.CharField(
        max_length=50,
        choices=PAID_STATUS_CHOICES,
        default="not_paid",
        verbose_name="Thanh toán",
    )
    done_status = models.CharField(
        max_length=50,
        choices=DONE_STATUS_CHOICES,
        default="not_done",
        verbose_name="Sửa chữa",
    )

    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="Ngày tạo phiếu"
    )

    part_providers = models.TextField(
        verbose_name="Các nhà cung cấp", default="", null=True, blank=True
    )

    def __str__(self):
        return f"Mã {self.repair_code} - Xe {self.vehicle}"

    def save(self, *args, **kwargs):
        # if self.user changed => skip (just save the frist user)

        super().save()
        self.repair_code = "SC" + str(self.pk).zfill(4)
        # Get all related vehicle parts
        vehicle_parts = VehicleMaintenanceRepairPart.objects.filter(
            vehicle_maintenance=self
        )
        # Calculate the total maintenance amount
        total_amount = 0
        for vehicle_part in vehicle_parts:
            part_amount = vehicle_part.repair_part.part_price * vehicle_part.quantity
            total_amount += part_amount

        self.maintenance_amount = total_amount

        # Check if all parts are received, if yes => received_status = 'received'
        if vehicle_parts.filter(received_status="not_received").count() == 0:
            self.received_status = "received"
        else:
            self.received_status = "not_received"

        # Check if all parts are paid, if yes => paid_status = 'paid'
        all_provider_payment_states = self.calculate_all_provider_payment_states()
        total_purchase_amount = 0
        total_transferred_amount = 0
        total_debt_amount = 0
        self.part_providers = ""

        for provider_id, provider_payment_state in all_provider_payment_states.items():
            total_purchase_amount += provider_payment_state["purchase_amount"]
            total_transferred_amount += provider_payment_state["transferred_amount"]
            total_debt_amount += provider_payment_state["debt_amount"]

            part_provider = PartProvider.objects.get(pk=provider_id)
            self.part_providers += "- " + part_provider.name + "\n"
        self.part_providers.strip()

        if total_purchase_amount == 0:
            self.paid_status = "not_paid"
        else:
            if total_debt_amount == 0:
                self.paid_status = "paid"
            elif total_debt_amount > 0 and total_transferred_amount > 0:
                self.paid_status = "partial_paid"
            else:
                self.paid_status = "not_paid"

        # Check if all parts are done, if yes => done_status = 'done'
        if vehicle_parts.filter(done_status="not_done").count() == 0:
            self.done_status = "done"
        else:
            self.done_status = "not_done"
        super().save()

        # prevent recursion
        from_payment_record = kwargs.get("from_payment_record", None)
        if from_payment_record:
            return

        # Create or update payment records
        if self.approval_status == "approved":
            all_provider_payment_state = self.calculate_all_provider_payment_states()

            # Get all payment records which has vehicle_maintenance = self and provider_id = provider_id
            for provider_id in all_provider_payment_state:
                payment_records = PaymentRecord.objects.filter(
                    vehicle_maintenance=self, provider_id=provider_id
                ).order_by("id")
                if len(payment_records) == 0:
                    payment_record, created = PaymentRecord.objects.get_or_create(
                        vehicle_maintenance=self, provider_id=provider_id
                    )
                    payment_record.previous_debt = all_provider_payment_state[
                        provider_id
                    ]["debt_amount"]
                    payment_record.purchase_amount = all_provider_payment_state[
                        provider_id
                    ]["purchase_amount"]
                    payment_record.save()
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
                        payment_record.purchase_amount = all_provider_payment_state[
                            provider_id
                        ]["purchase_amount"]
                        payment_record.debt = (
                            previous_debt - payment_record.transferred_amount
                        )
                        payment_record.save()

        elif self.approval_status == "rejected":
            PaymentRecord.objects.filter(vehicle_maintenance=self).delete()

    def calculate_all_provider_payment_states(self):
        # get all the parts in this vehicle maintenance
        vehicle_parts = VehicleMaintenanceRepairPart.objects.filter(
            vehicle_maintenance=self
        )
        # get all the providers in this vehicle maintenance
        provider_ids = vehicle_parts.values_list(
            "repair_part__part_provider", flat=True
        ).distinct()
        provider_ids = set(provider_ids)
        all_provider_payment_state = {}
        for provider_id in provider_ids:
            provider = PartProvider.objects.get(pk=provider_id)
            # calculate the purchase amount
            purchase_amount = 0
            provider_vehicle_parts = vehicle_parts.filter(
                repair_part__part_provider=provider
            )
            for provider_vehicle_part in provider_vehicle_parts:
                purchase_amount += (
                    provider_vehicle_part.repair_part.part_price
                    * provider_vehicle_part.quantity
                )

            # calculate the transferred amount
            transferred_amount = 0
            payment_records = PaymentRecord.objects.filter(
                vehicle_maintenance=self, provider=provider
            )
            for payment_record in payment_records:
                transferred_amount += payment_record.transferred_amount

            # calculate the debt amount
            debt_amount = purchase_amount - transferred_amount

            # calculate the debt amount
            debt_amount = purchase_amount - transferred_amount

            state = {
                "purchase_amount": purchase_amount,
                "transferred_amount": transferred_amount,
                "debt_amount": debt_amount,
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
        vehicle_parts = VehicleMaintenanceRepairPart.objects.filter(
            vehicle_maintenance=self, repair_part__isnull=False
        )
        # Put into dict of groups of providers
        vehicle_parts_dict = {}
        for vehicle_part in vehicle_parts:
            if vehicle_part.repair_part.part_provider not in vehicle_parts_dict:
                vehicle_parts_dict[vehicle_part.repair_part.part_provider] = []
            vehicle_parts_dict[vehicle_part.repair_part.part_provider].append(
                vehicle_part
            )
        return vehicle_parts_dict

    @classmethod
    def get_repair_part_list(cls):
        part_list = RepairPart.objects.all()
        return part_list

    @classmethod
    def get_display_fields(self):
        fields = [
            "repair_code",
            "vehicle",
            "maintenance_category",
            "approval_status",
            "received_status",
            "paid_status",
            "done_status",
            "part_providers",
            "maintenance_amount",
            "from_date",
            "to_date",
            "created_at",
            "user",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class MaintenanceImage(BaseModel):
    vietnamese_name = "Hình ảnh sửa chữa"
    vehicle_maintenance = models.ForeignKey(
        VehicleMaintenance,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Phiếu sửa chữa",
    )
    image = models.ImageField(
        upload_to="maintenance/",
        verbose_name="Hình ảnh",
        default="",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Mã sữa chưa "{self.vehicle_maintenance}"'


class PartProvider(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "NCC phụ tùng (sửa chữa)"
    # Driver Information Fields
    name = models.CharField(
        max_length=255, verbose_name="Tên nhà cung cấp", unique=True
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
        verbose_name="Tổng tiền mua", default=0, validators=[MinValueValidator(0)]
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
        # calculate_payment_states
        # Get all VehicleMaintenanceRepairPart
        repair_parts = VehicleMaintenanceRepairPart.objects.filter(
            repair_part__part_provider=self
        )
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
        super().save(*args, **kwargs)

    def get_related_orders(self):
        # Lấy tất cả các phụ tùng trong phiếu sửa chữa có nhà cung cấp là self
        vehicle_maintenance_repair_parts = VehicleMaintenanceRepairPart.objects.filter(
            repair_part__part_provider=self
        )

        # Lấy danh sách các phiếu sửa chữa từ các phụ tùng đã tìm được
        vehicle_maintenance_ids = vehicle_maintenance_repair_parts.values_list(
            "vehicle_maintenance", flat=True
        ).distinct()

        # Truy vấn tất cả các phiếu sửa chữa có ID trong danh sách
        maintenance_records = VehicleMaintenance.objects.filter(
            id__in=vehicle_maintenance_ids
        ).order_by("-created_at")
        print("hell")
        return maintenance_records


class RepairPart(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Phụ tùng (sửa chữa)"

    class Meta:
        ordering = ["-created_at", "part_provider", "part_name"]

    part_provider = models.ForeignKey(
        PartProvider,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Nhà cung cấp",
    )
    vehicle_type = models.ForeignKey(
        VehicleType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Loại xe",
    )
    part_number = models.CharField(
        max_length=255, verbose_name="Mã phụ tùng", unique=True
    )
    part_name = models.CharField(max_length=255, verbose_name="Tên đầy đủ")
    part_price = models.IntegerField(
        verbose_name="Đơn giá", default=0, validators=[MinValueValidator(0)]
    )
    unit = models.CharField(
        max_length=255, verbose_name="Đơn vị", default="cái", null=True, blank=True
    )
    image = models.ImageField(
        verbose_name="Hình ảnh", default="", null=True, blank=True
    )
    note = models.TextField(verbose_name="Mô tả", default="", null=True, blank=True)
    valid_from = models.DateField(verbose_name="Ngày áp dụng", default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.part_number} - {self.part_name} - Áp dụng từ {self.valid_from}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "part_provider",
            "part_number",
            "part_name",
            "part_price",
            "image",
            "note",
            "valid_from",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class VehicleMaintenanceRepairPart(BaseModel):
    vietnamese_name = "Phụ tùng trong phiếu sửa chữa"
    RECEIVED_STATUS_CHOICES = (
        ("received", "Đã nhận"),
        ("not_received", "Chưa nhận"),
    )

    DONE_STATUS_CHOICES = (
        ("done", "Xong"),
        ("not_done", "Chưa xong"),
    )

    vehicle_maintenance = models.ForeignKey(
        VehicleMaintenance,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Phiếu sửa chữa",
    )
    repair_part = models.ForeignKey(
        RepairPart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Bộ phận",
    )
    quantity = models.IntegerField(
        verbose_name="Số lượng", default=0, validators=[MinValueValidator(0)]
    )
    received_status = models.CharField(
        max_length=50,
        choices=RECEIVED_STATUS_CHOICES,
        default="not_received",
        verbose_name="Trạng thái nhận hàng",
    )
    done_status = models.CharField(
        max_length=50,
        choices=DONE_STATUS_CHOICES,
        default="not_done",
        verbose_name="Trạng thái xong sửa chữa",
    )

    def __str__(self):
        return f"Mã phiếu {self.vehicle_maintenance.repair_code} - {self.repair_part.part_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        provider = self.repair_part.part_provider
        provider.save()

    def delete(self, *args, **kwargs):
        provider = self.repair_part.part_provider
        super().delete(*args, **kwargs)
        provider.save()

    @classmethod
    def get_maintenance_amount(cls, vehicle, from_date, to_date):
        total_amount = 0
        vehicle_maintenances = VehicleMaintenance.objects.filter(
            vehicle=vehicle, from_date__gte=from_date, from_date__lte=to_date
        )
        for vehicle_maintenance in vehicle_maintenances:
            repair_parts = VehicleMaintenanceRepairPart.objects.filter(
                vehicle_maintenance=vehicle_maintenance
            )
            for repair_part in repair_parts:
                if repair_part.received_status == "received":
                    total_amount += (
                        repair_part.repair_part.part_price * repair_part.quantity
                    )

        return total_amount


class PaymentRecord(BaseModel):
    allow_display = True
    excel_downloadable = True
    vietnamese_name = "Thanh toán (sửa chữa)"

    class Meta:
        ordering = ["vehicle_maintenance", "provider", "-id"]

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
    vehicle_maintenance = models.ForeignKey(
        VehicleMaintenance,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Phiếu sửa chữa",
    )
    provider = models.ForeignKey(
        PartProvider,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Nhà cung cấp",
    )
    status = models.CharField(
        max_length=50,
        choices=PAID_STATUS_CHOICES,
        default="not_requested",
        verbose_name="Trạng thái thanh toán",
    )

    purchase_amount = models.IntegerField(
        verbose_name="Tổng tiền trên phiếu sửa chữa",
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
        verbose_name="Hình ảnh", upload_to="images/finance/", blank=True, null=True
    )
    image2 = models.ImageField(
        verbose_name="Hình ảnh", upload_to="images/finance/", blank=True, null=True
    )

    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    def __str__(self):
        return (
            f"Mã phiếu sửa chữa {self.vehicle_maintenance} - ngày tạo {self.created_at}"
        )

    @classmethod
    def get_display_fields(self):
        fields = [
            "vehicle_maintenance",
            "provider",
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
            "created_at",
        ]
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

        self.user = self.vehicle_maintenance.user

        super().save(*args, **kwargs)
        self.provider.save()

        # extract the vehicle maintenance and provider
        vehicle_maintenance = self.vehicle_maintenance
        provider = self.provider
        # get all payment records
        last_payment_record = (
            PaymentRecord.objects.filter(
                vehicle_maintenance=vehicle_maintenance, provider=provider
            )
            .order_by("id")
            .last()
        )
        # if self = last payment record
        if last_payment_record == self and self.lock == True and self.debt != 0:
            # create new payment record
            new_payment_record = PaymentRecord.objects.create(
                vehicle_maintenance=vehicle_maintenance, provider=provider
            )
            new_payment_record.previous_debt = self.debt
            new_payment_record.purchase_amount = self.purchase_amount
            new_payment_record.debt = self.debt
            new_payment_record.save()

        # save vehicle maintenance to update payment status
        vehicle_maintenance.save(from_payment_record=True)

    def clean(self):
        errors = ""
        if self.requested_amount > self.previous_debt:
            errors += f'- Số tiền đề nghị phải nhỏ hơn hoặc bằng nợ kì trước {format(self.previous_debt, ",d")}.\n'

        if self.requested_amount == 0 and self.transferred_amount > 0:
            errors += f"- Chưa thanh toán khi chưa có đề nghị.\n"

        # if self.transferred_amount < self.requested_amount and self.transferred_amount > 0:
        #     errors += (f'- Số tiền thanh toán phải lớn hơn hoặc bằng số tiền đề nghị {format(self.requested_amount, ",d")}.\n')
        if self.transferred_amount > self.previous_debt:
            errors += f'- Số tiền thanh toán phải nhỏ hơn hoặc bằng nợ kì trước {format(self.previous_debt, ",d")}.\n'
        if self.payment_date < self.requested_date:
            errors += f'- Ngày thanh toán phải lớn hơn hoặc bằng ngày đề nghị {self.requested_date.strftime("%d/%m/%Y")}.\n'

        if self.lock and self.transferred_amount == 0:
            errors += f"- Không thể khóa phiếu thanh toán khi chưa thanh toán.\n"

        if errors:
            raise ValidationError(errors)

    def total_transfered_amount(self):
        # Get all payment records with same vehicle_maintenance and provider and lock = True
        payment_records = PaymentRecord.objects.filter(
            vehicle_maintenance=self.vehicle_maintenance,
            provider=self.provider,
            lock=True,
        )
        # Calculate the sum of transferred_amount
        total_transfered_amount = sum(
            record.transferred_amount for record in payment_records
        )
        return total_transfered_amount
