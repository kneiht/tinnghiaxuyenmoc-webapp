from django.core.validators import MinValueValidator
from django.utils import timezone

from .base import models, BaseModel
from .project import Project
from django.contrib.auth.models import User

class SupplyProvider(BaseModel):
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



class BaseSupply(BaseModel):
    MATERIAL_CHOICES = (
        ('Vật tư thông thường', 'Vật tư thông thường'),
        ('Vật tư sắt thép', 'Vật tư sắt thép'),
        ('Vật tư cát, đá, xi măng', 'Vật tư cát, đá, xi măng'),
        ('Vật tư bê tông', 'Vật tư bê tông'),
        ('Vật tư nhựa', 'Vật tư nhựa'),
        ('Vật tư biển báo, cọc tiêu, cơ khí', 'Vật tư biển báo, cọc tiêu, cơ khí'),
    )

    class Meta:
        ordering = ['supply_number', 'supply_name']
    material_type = models.CharField(max_length=50, choices=MATERIAL_CHOICES, default="Vật tư thông thường", verbose_name="Nhóm vật tư")
    supply_number = models.CharField(max_length=255, verbose_name="Mã vật tư", unique=True)
    supply_name = models.CharField(max_length=255, verbose_name="Tên đầy đủ")
    unit = models.CharField(max_length=255, verbose_name="Đơn vị", default="cái", null=True, blank=True)
    image = models.ImageField(verbose_name="Hình ảnh", default="", null=True, blank=True)
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.supply_number} - {self.supply_name} - {self.unit}'

    @classmethod
    def get_display_fields(self):
        fields = ['supply_number', 'material_type', 'supply_name', 'unit', 'image', 'note']
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
            image=self.image
        )
        CostEstimation.objects.filter(base_supply=self).update(
            material_type=self.material_type,
            supply_number=self.supply_number,
            supply_name=self.supply_name,
            unit=self.unit
        )
    

 

class DetailSupply(BaseModel):
    class Meta:
        ordering = ['supply_provider', 'material_type', 'supply_number']
    supply_provider = models.ForeignKey(SupplyProvider, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Nhà cung cấp")
    base_supply = models.ForeignKey(BaseSupply, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vật tư")

    supply_price = models.IntegerField(verbose_name="Đơn giá", default=0, validators=[MinValueValidator(0)])

    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    valid_from = models.DateField(verbose_name="Ngày áp dụng", default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    # From BaseSupply
    material_type = models.CharField(max_length=50, verbose_name="Nhóm vật tư")
    supply_number = models.CharField(max_length=255, verbose_name="Mã vật tư", null=True, blank=True)
    supply_name = models.CharField(max_length=255, verbose_name="Tên đầy đủ", null=True, blank=True)
    unit = models.CharField(max_length=255, verbose_name="Đơn vị", default="cái", null=True, blank=True)
    image = models.ImageField(verbose_name="Hình ảnh", default="", null=True, blank=True)
    # end From BaseSupply


    def __str__(self):
        return f'{self.supply_provider} - {self.supply_number} - {self.supply_name}'

    @classmethod
    def get_display_fields(self):
        fields = ['supply_provider', 'supply_number', 'material_type', 'supply_name', 'supply_price', 'unit', 'image', 'note', 'valid_from']
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


class CostEstimation(BaseModel):
    class Meta:
        ordering = ['project', 'material_type', 'supply_number']
        unique_together = ('project', 'base_supply')  # Enforces uniqueness

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Dự án")

    # Danh mục công việc
    category = models.CharField(max_length=1000, default="Chưa phân loại", verbose_name="Nhóm công việc")

    base_supply = models.ForeignKey(BaseSupply, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vật tư")


    # From BaseSupply
    material_type = models.CharField(max_length=50, verbose_name="Nhóm vật tư")
    supply_number = models.CharField(max_length=255, verbose_name="Mã vật tư", null=True, blank=True)
    supply_name = models.CharField(max_length=255, verbose_name="Tên đầy đủ", null=True, blank=True)
    unit = models.CharField(max_length=255, verbose_name="Đơn vị", default="cái", null=True, blank=True)
    # end From BaseSupply

    quantity = models.FloatField(default=0.0, validators=[MinValueValidator(0)], verbose_name="Khối lượng")
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    @classmethod
    def get_display_fields(self):
        fields = ['category', 'material_type', 'supply_number', 'supply_name', 'unit', 'quantity', 'note']
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
        super().save()





class SupplyOrder(BaseModel):

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
        ('partial_paid', 'T.toán một phần'),
    )

    class Meta:
        ordering = ['-created_at']


    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người tạo")
    order_code = models.CharField(max_length=255, verbose_name="Mã phiếu", default="", null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Dự án")

    order_amount = models.IntegerField(verbose_name="Tổng tiền", default=0, validators=[MinValueValidator(0)])

    approval_status = models.CharField(max_length=50, choices=APPROVAL_STATUS_CHOICES, default='scratch', verbose_name="Duyệt")
    received_status = models.CharField(max_length=50, choices=RECEIVED_STATUS_CHOICES, default='not_received', verbose_name="Nhận hàng")
    paid_status = models.CharField(max_length=50, choices=PAID_STATUS_CHOICES, default='not_paid', verbose_name="Thanh toán")

    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo phiếu")

    supply_providers = models.TextField(verbose_name="Các nhà cung cấp", default="", null=True, blank=True)

    def save(self, *args, **kwargs):
        self.repair_code = "#" + str(self.pk).zfill(4)
        super().save()

    @classmethod
    def get_display_fields(self):
        fields = [
            'order_code', 'project', 'approval_status', 
            'received_status', 'paid_status', 'supply_providers', 'order_amount', 'note', 'created_at', 'user']
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def __str__(self):
        return self.order_code

