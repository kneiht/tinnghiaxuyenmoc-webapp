from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator
from django.utils import timezone

from .base import models, BaseModel
from .project import Project
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class SupplyProvider(BaseModel):
    allow_display = True
    vietnamese_name = "Nhà cung cấp vật tư"
    excel_downloadable = True
    excel_uploadable = True
    excel_columns = [
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
        # Get all SupplyOrderSupply records for this provider
        order_supplies = SupplyOrderSupply.objects.filter(
            detail_supply__supply_provider=self
        )

        # Calculate total purchase amount
        purchase_amount = 0
        for order_supply in order_supplies:
            if order_supply.detail_supply:
                purchase_amount += (
                    order_supply.detail_supply.supply_price * order_supply.quantity
                )

        # Calculate total transferred amount from payment records
        transferred_amount = 0
        payment_records = SupplyPaymentRecord.objects.filter(provider=self)
        for payment_record in payment_records:
            transferred_amount += payment_record.transferred_amount

        # Calculate outstanding debt
        debt_amount = purchase_amount - transferred_amount

        # Update provider's financial fields
        self.total_purchase_amount = purchase_amount
        self.total_transferred_amount = transferred_amount
        self.total_outstanding_debt = debt_amount
        super().save(*args, **kwargs)


class SupplyBrand(BaseModel):
    allow_display = True
    vietnamese_name = "Thương hiệu vật tư"
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

class DetailSupplyKey:
    provider: SupplyProvider
    brand: SupplyBrand
    
    def __init__(self, provider: SupplyProvider, brand: SupplyBrand):
        self.provider = provider
        self.brand = brand

    def __str__(self):
        return f"{self.provider.name} - Thương hiệu: {self.brand.name}"
    
class BaseSupply(BaseModel):
    allow_display = True
    vietnamese_name = "Vật tư"
    MATERIAL_CHOICES = (
        ("Vật tư thông thường", "Vật tư thông thường"),
        ("Vật tư sắt thép", "Vật tư sắt thép"),
        ("Vật tư cát, đá, xi măng", "Vật tư cát, đá, xi măng"),
        ("Vật tư bê tông", "Vật tư bê tông"),
        ("Vật tư nhựa", "Vật tư nhựa"),
        ("Vật tư điện", "Vật tư điện"),
        ("Vật tư nước", "Vật tư nước"),
        ("Cây xanh", "Cây xanh"),
        ("Vật tư đặc thù", "Vật tư đặc thù"),
        ("Vật tư biển báo, cọc tiêu, cơ khí", "Vật tư biển báo, cọc tiêu, cơ khí"),
        ("Vật tư phụ/ Biện pháp thi công", "Vật tư phụ/ Biện pháp thi công"),
        ("Vật tư gồm nhân công thi công", "Vật tư gồm nhân công thi công"),
    )

    class Meta:
        ordering = ["supply_number", "supply_name"]

    material_type = models.CharField(
        max_length=50,
        choices=MATERIAL_CHOICES,
        default="Vật tư thông thường",
        verbose_name="Nhóm vật tư",
    )
    supply_number = models.CharField(
        max_length=255, verbose_name="Mã vật tư", unique=True
    )
    supply_name = models.CharField(max_length=255, verbose_name="Tên đầy đủ")
    unit = models.CharField(
        max_length=255, verbose_name="Đơn vị", default="cái", null=True, blank=True
    )
    image = models.ImageField(
        verbose_name="Hình ảnh vật tư", default="", null=True, blank=True
    )
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.supply_number} - {self.supply_name}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "supply_number",
            "material_type",
            "supply_name",
            "unit",
            "image",
            "note",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        DetailSupply.objects.filter(base_supply=self).update(
            material_type=self.material_type,
            supply_number=self.supply_number,
            supply_name=self.supply_name,
            unit=self.unit,
            image=self.image,
        )
        CostEstimation.objects.filter(base_supply=self).update(
            material_type=self.material_type,
            supply_number=self.supply_number,
            supply_name=self.supply_name,
            unit=self.unit,
        )

    def get_provider_and_brands(self):
        """Get list of providers that have this base supply"""
        detail_supplies = DetailSupply.objects.filter(base_supply=self)
        provider_and_brands = []
        provider_and_brand_ids = detail_supplies.values_list(
            "supply_provider", "supply_brand"
        ).distinct()
        for provider, brand in provider_and_brand_ids:
            if provider and brand:
                provider = SupplyProvider.objects.get(pk=provider)
                brand = SupplyBrand.objects.get(pk=brand)
                provider_and_brands.append((provider, brand))
        print("provider_and_brands", provider_and_brands)
        return provider_and_brands

    def get_list_of_detail_supplies_of_a_provider_and_a_brand(self, provider, brand):
        """Get list of detail supplies that have this base supply"""
        return DetailSupply.objects.filter(
            base_supply=self, supply_provider=provider, supply_brand=brand
        ).order_by("-valid_from")

    def get_dict_of_detail_supplies(self):
        provider_and_brands = self.get_provider_and_brands()
        print("provider_and_brands")

        detail_supply_dict = {}
        for provider, brand in provider_and_brands:
            detail_supplies = self.get_list_of_detail_supplies_of_a_provider_and_a_brand(
                provider, brand
            )
            detail_supply_dict[DetailSupplyKey(provider, brand)] = detail_supplies
        # printdebug the dict
        return detail_supply_dict


class DetailSupply(BaseModel):
    allow_display = True
    vietnamese_name = "Vật tư chi tiết"

    class Meta:
        ordering = ["supply_provider", "supply_brand", "material_type", "supply_number"]

    supply_provider = models.ForeignKey(
        SupplyProvider,
        on_delete=models.CASCADE,
        verbose_name="Nhà cung cấp",
    )
    supply_brand = models.ForeignKey(
        SupplyBrand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Thương hiệu",
    )

    base_supply = models.ForeignKey(
        BaseSupply,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Vật tư",
    )

    supply_price = models.IntegerField(
        verbose_name="Đơn giá", default=0, validators=[MinValueValidator(0)]
    )

    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    valid_from = models.DateField(verbose_name="Ngày áp dụng", default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    # From BaseSupply
    material_type = models.CharField(max_length=50, verbose_name="Nhóm vật tư")
    supply_number = models.CharField(
        max_length=255, verbose_name="Mã vật tư", null=True, blank=True
    )
    supply_name = models.CharField(
        max_length=1000, verbose_name="Tên đầy đủ", null=True, blank=True
    )
    unit = models.CharField(
        max_length=255, verbose_name="Đơn vị", default="cái", null=True, blank=True
    )
    image = models.ImageField(
        verbose_name="Hình ảnh vật tư", default="", null=True, blank=True
    )

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
        return f"{self.supply_provider} - {self.supply_number} - {self.supply_name}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "supply_provider",
            "supply_brand",
            "supply_number",
            "material_type",
            "supply_name",
            "supply_price",
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
        if self.base_supply:
            self.material_type = self.base_supply.material_type
            self.supply_number = self.base_supply.supply_number
            self.supply_name = self.base_supply.supply_name
            self.unit = self.base_supply.unit
            self.image = self.base_supply.image
        super().save()

    def clean(self):
        # if update => not allow to update
        if self.pk:
            raise ValidationError("Vui lòng xóa vật tư chi tiết này và tạo mới vì vật tư chi tiết không cho thay đổi thông tin.")
        super().clean()

class CostEstimation(BaseModel):
    allow_display = True
    vietnamese_name = "Dự toán vật tư"

    class Meta:
        ordering = ["project", "material_type", "supply_number"]
        unique_together = ("project", "base_supply")  # Enforces uniqueness

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Dự án")

    base_supply = models.ForeignKey(
        BaseSupply,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Vật tư",
    )

    # From BaseSupply
    material_type = models.CharField(max_length=50, verbose_name="Nhóm vật tư")
    supply_number = models.CharField(
        max_length=255, verbose_name="Mã vật tư", null=True, blank=True
    )
    supply_name = models.CharField(
        max_length=255, verbose_name="Tên đầy đủ", null=True, blank=True
    )
    unit = models.CharField(
        max_length=255, verbose_name="Đơn vị", default="cái", null=True, blank=True
    )
    # end From BaseSupply

    quantity = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0)],
        verbose_name="Khối lượng dự toán",
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
        verbose_name="Khối lượng đã nhận",
    )
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return (
            f"Dự án {self.project} - Vật tư {self.supply_number} - {self.supply_name}"
        )

    @classmethod
    def get_display_fields(self):
        fields = [
            "material_type",
            "supply_number",
            "supply_name",
            "unit",
            "quantity",
            "ordered_quantity",
            "orderable_quantity",
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

        if self.base_supply:
            self.material_type = self.base_supply.material_type
            self.supply_number = self.base_supply.supply_number
            self.supply_name = self.base_supply.supply_name
            self.unit = self.base_supply.unit

        self.orderable_quantity = self.get_orderable_quantity()
        self.ordered_quantity = self.get_ordered_quantity()
        self.paid_quantity = self.get_paid_quantity()
        self.received_quantity = self.get_received_quantity()
        super().save()

    # estimate_quantity
    def get_estimate_quantity(self):
        return self.quantity

    def get_orderable_quantity(self):
        # If marterial_type is "Vật tư phụ / Biện pháp thi công", return 999999
        if self.material_type == "Vật tư phụ / Biện pháp thi công":
            return 9999999
        # Get all supply orders for this project and supply
        existing_orders = SupplyOrderSupply.objects.filter(
            supply_order__project=self.project, base_supply=self.base_supply
        )
        # Calculate total ordered quantity
        total_ordered = sum(order.quantity for order in existing_orders)
        # Maximum orderable quantity is the difference between estimated and ordered
        max_orderable = self.quantity - total_ordered
        return max_orderable

    def get_ordered_quantity(self):
        # Get all supply orders for this project and supply
        existing_orders = SupplyOrderSupply.objects.filter(
            supply_order__project=self.project, base_supply=self.base_supply
        )
        # Calculate total ordered quantity
        total_ordered = sum(order.quantity for order in existing_orders)
        return total_ordered

    def get_paid_quantity(self):
        # Get all supply orders for this project and supply
        existing_orders = SupplyOrderSupply.objects.filter(
            supply_order__project=self.project, base_supply=self.base_supply
        )
        total_paid = sum(order.paid_quantity for order in existing_orders)
        return total_paid

    def get_received_quantity(self):
        # Get all supply orders for this project and supply
        existing_orders = SupplyOrderSupply.objects.filter(
            supply_order__project=self.project, base_supply=self.base_supply
        )
        total_received = sum(order.received_quantity for order in existing_orders)
        for order in existing_orders:
            print("order", order, order.received_quantity)
        print("total_received", total_received)
        return total_received


class SupplyOrder(BaseModel):
    allow_display = True
    vietnamese_name = "Đặt vật tư"

    APPROVAL_STATUS_CHOICES = (
        ("scratch", "Bảng nháp"),
        ("wait_for_approval", "Chờ duyệt"),
        ("approved", "Đã duyệt"),
        ("rejected", "Từ chối"),
    )

    RECEIVED_STATUS_CHOICES = (
        ("received", "Đã nhận"),
        ("not_received", "Chưa nhận"),
        ("partial_received", "Nhận một phần"),
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
        verbose_name="Nhận hàng",
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
    supply_providers = models.TextField(
        verbose_name="Các nhà cung cấp", default="", null=True, blank=True
    )

    def __str__(self):
        return f"{self.order_code}"

    def save(self, *args, **kwargs):
        # Skip if user changed (keep first user)
        if self.pk:
            old_instance = SupplyOrder.objects.get(pk=self.pk)
            if old_instance.user:
                self.user = old_instance.user
        self.order_code = "#" + str(self.pk).zfill(4)
        super().save()

        # Get all related supply orders
        order_supplies = SupplyOrderSupply.objects.filter(supply_order=self)

        # Calculate total order amount
        total_amount = 0
        for order_supply in order_supplies:
            if order_supply.detail_supply:
                supply_amount = (
                    order_supply.detail_supply.supply_price * order_supply.quantity
                )
                total_amount += supply_amount

        self.order_amount = total_amount

        # Check received status
        if order_supplies.count()>0 and order_supplies.count == order_supplies.filter(received_status="received").count():
            self.received_status = "received"
        elif order_supplies.count()>0 and order_supplies.filter(received_status="partial_received").count() > 0:
            self.received_status = "partial_received"
        else:
            self.received_status = "not_received"

        # Check payment status and update providers list
        all_provider_payment_states = self.calculate_all_provider_payment_states()
        total_purchase_amount = 0
        total_transferred_amount = 0
        total_debt_amount = 0
        self.supply_providers = ""

        for provider_id, provider_payment_state in all_provider_payment_states.items():
            total_purchase_amount += provider_payment_state["purchase_amount"]
            total_transferred_amount += provider_payment_state["transferred_amount"]
            total_debt_amount += provider_payment_state["debt_amount"]

            provider = SupplyProvider.objects.get(pk=provider_id)
            self.supply_providers += "- " + provider.name + "\n"
        self.supply_providers = self.supply_providers.strip()

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
                payment_records = SupplyPaymentRecord.objects.filter(
                    supply_order=self, provider_id=provider_id
                ).order_by("id")

                if len(payment_records) == 0:
                    payment_record = SupplyPaymentRecord.objects.create(
                        supply_order=self,
                        provider_id=provider_id,
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
            SupplyPaymentRecord.objects.filter(supply_order=self).delete()

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
        # Get all supplies in this supply order
        order_supplies = SupplyOrderSupply.objects.filter(supply_order=self)

        # Get all providers in this supply order
        provider_ids = order_supplies.values_list(
            "detail_supply__supply_provider", flat=True
        ).distinct()
        provider_ids = set(provider_ids)

        all_provider_payment_state = {}
        for provider_id in provider_ids:
            if not provider_id:  # Skip if provider is None
                continue

            provider = SupplyProvider.objects.get(pk=provider_id)

            # Calculate purchase amount
            purchase_amount = 0
            provider_supplies = order_supplies.filter(
                detail_supply__supply_provider=provider
            )
            for supply in provider_supplies:
                if supply.detail_supply:
                    purchase_amount += (
                        supply.detail_supply.supply_price * supply.quantity
                    )

            # Calculate transferred amount
            transferred_amount = 0
            payment_records = SupplyPaymentRecord.objects.filter(
                supply_order=self, provider=provider
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

    def get_supply_order_base_supply_list(self):
        order_supplies = SupplyOrderSupply.objects.filter(
            supply_order=self, base_supply__isnull=False
        )
        print(order_supplies)
        return order_supplies

    def get_supply_order_detail_supply_list(self):
        order_supplies = SupplyOrderSupply.objects.filter(
            supply_order=self, detail_supply__isnull=False
        )
        # Put into dict of groups of providers
        supply_order_supply_dict = {}
        for order_supply in order_supplies:
            if (
                order_supply.detail_supply.supply_provider
                not in supply_order_supply_dict
            ):
                supply_order_supply_dict[order_supply.detail_supply.supply_provider] = (
                    []
                )
            supply_order_supply_dict[order_supply.detail_supply.supply_provider].append(
                order_supply
            )
        return supply_order_supply_dict





class SupplyOrderSupply(BaseModel):
    vietnamese_name = "Vật tư trong phiếu đặt"
    RECEIVED_STATUS_CHOICES = (
        ("received", "Đã nhận"),
        ("not_received", "Chưa nhận"),
        ("partial_received", "Đã nhận một phần"),
    )
    # id = models.IntegerField(primary_key=True)
    supply_order = models.ForeignKey(
        SupplyOrder,
        on_delete=models.CASCADE,
        verbose_name="Phiếu mua hàng",
        null=True,
        blank=True,
    )
    base_supply = models.ForeignKey(
        BaseSupply,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Vật tư",
    )
    detail_supply = models.ForeignKey(
        DetailSupply,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Vật tư chi tiết",
    )
    quantity = models.FloatField(
        verbose_name="Số lượng", default=0.0, validators=[MinValueValidator(0)]
    )
    paid_quantity = models.FloatField(
        verbose_name="Số lượng đã T.toán",
        default=0.0,
        validators=[MinValueValidator(0)],
    )
    received_quantity = models.FloatField(
        verbose_name="Số lượng đã nhận", default=0.0, validators=[MinValueValidator(0)]
    )
    received_status = models.CharField(
        max_length=50,
        choices=RECEIVED_STATUS_CHOICES,
        default="not_received",
        verbose_name="Trạng thái nhận hàng",
    )

    def __str__(self):
        return f"{self.supply_order.order_code} - {self.base_supply}"

    def delete(self, *args, **kwargs):
        provider = None
        if self.detail_supply:
            provider = self.detail_supply.supply_provider
        super().delete(*args, **kwargs)
        if provider:
            provider.save()

    def save(self, *args, **kwargs):
        # Get old provider before saving
        old_provider = None
        if self.pk:
            old_instance = SupplyOrderSupply.objects.get(pk=self.pk)
            if old_instance.detail_supply:
                old_provider = old_instance.detail_supply.supply_provider

        # Get new provider after saving
        new_provider = None
        if self.detail_supply:
            new_provider = self.detail_supply.supply_provider

        # Update payment states for both old and new providers
        if old_provider and old_provider != new_provider:
            old_provider.save()
        if new_provider:
            new_provider.save()

        # update cost estimation
        cost_estimation = CostEstimation.objects.filter(
            project=self.supply_order.project, base_supply=self.base_supply
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


    def estimate_quantity(self):
        cost_estimation = CostEstimation.objects.filter(
            project=self.supply_order.project, base_supply=self.base_supply
        ).first()
        if cost_estimation:
            return cost_estimation.quantity
        else:
            return 0.0

    def orderable_quantity(self):
        # Get cost estimation for this project and supply
        cost_estimation = CostEstimation.objects.filter(
            project=self.supply_order.project, base_supply=self.base_supply
        ).first()
        orderable_quantity = cost_estimation.get_orderable_quantity() + self.quantity
        return orderable_quantity


class SupplyPaymentRecord(BaseModel):
    allow_display = True
    vietnamese_name = "Thanh toán vật tư"

    class Meta:
        ordering = ["supply_order", "provider", "-id"]

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

    supply_order = models.ForeignKey(
        SupplyOrder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Phiếu mua hàng",
    )
    provider = models.ForeignKey(
        SupplyProvider,
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
        return (
            f"Mã đơn vật tư {self.supply_order} - Ngày tạo thanh toán {self.created_at}"
        )

    @classmethod
    def get_display_fields(self):
        fields = [
            "project",
            "supply_order",
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
        ]
        return [field for field in fields if hasattr(self, field)]

    def save(self, *args, **kwargs):
        self.project = self.supply_order.project

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
        self.user = self.supply_order.user

        super().save(*args, **kwargs)
        self.provider.save()

        # Extract supply order and provider
        supply_order = self.supply_order
        provider = self.provider

        # Get last payment record for this supply order and provider
        last_payment_record = (
            SupplyPaymentRecord.objects.filter(
                supply_order=supply_order, provider=provider
            )
            .order_by("id")
            .last()
        )

        # Create new payment record if this is the last one, it's locked, and has remaining debt
        if last_payment_record == self and self.lock and self.debt != 0:
            new_payment_record = SupplyPaymentRecord.objects.create(
                supply_order=supply_order,
                provider=provider,
                previous_debt=self.debt,
                purchase_amount=self.purchase_amount,
                debt=self.debt,
            )

        # Update supply order payment status
        supply_order.save(from_payment_record=True)

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
