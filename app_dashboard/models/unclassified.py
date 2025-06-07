import time
from datetime import date, datetime, time, timedelta

# Django imports
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import Max, Sum
from django.utils import timezone


from .base import models, BaseModel


def get_valid_date(date, start_date_mode="now"):
    try:
        date = datetime.strptime(date, "%Y-%m-%d").date()
    except:
        if start_date_mode == "now":
            date = timezone.now().date()
        elif start_date_mode == "none":
            date = None
            return date
    date = date.strftime("%Y-%m-%d")
    return date


class Location(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Địa điểm"
    TYPE_OF_LOCATION_CHOICES = [
        ("du_an", "Dự án/công trình"),
        ("kho_noi_bo", "Kho nội bộ"),
        ("bat_dong_san_noi_bo", "Bất động sản nội bộ"),
        ("khach_hang_dau_ra", "Khách hàng đầu ra"),
        ("khach_hang_dau_vao", "Khách hàng đầu vào"),
    ]
    name = models.CharField(max_length=500, verbose_name="Tên địa điểm")
    address = models.CharField(max_length=2000, verbose_name="Địa chỉ")
    type_of_location = models.CharField(
        max_length=255, choices=TYPE_OF_LOCATION_CHOICES, verbose_name="Loại hình"
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")
    note = models.TextField(blank=True, null=True, default="", verbose_name="Ghi chú")

    @classmethod
    def get_display_fields(self):
        fields = ["name", "address", "type_of_location", "note", "created_at"]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def __str__(self):
        return self.name


class VehicleType(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Loại xe"
    ALLOWED_TO_DISPLAY_IN_REVENUE_TABLE_CHOICES = (
        ("Cho phép", "Cho phép"),
        ("Không cho phép", "Không cho phép"),
    )

    class Meta:
        ordering = ["vehicle_type"]

    vehicle_type = models.CharField(max_length=255, verbose_name="Loại xe", unique=True)
    allowed_to_display_in_revenue_table = models.CharField(
        max_length=20,
        choices=ALLOWED_TO_DISPLAY_IN_REVENUE_TABLE_CHOICES,
        default="Cho phép",
        verbose_name="Cho phép lấy dữ liệu GPS",
    )
    note = models.TextField(blank=True, null=True, default="", verbose_name="Ghi chú")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.vehicle_type

    @classmethod
    def get_display_fields(self):
        fields = [
            "vehicle_type",
            "allowed_to_display_in_revenue_table",
            "note",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class StaffData(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Thông tin nhân viên"
    STATUS_CHOICES = (
        ("active", "Đang làm việc"),
        ("on_leave", "Nghỉ phép"),
        ("resigned", "Đã thôi việc"),
        ("terminated", "Bị sa thải"),
    )
    POSITION_CHOICES = (
        ("manager", "Quản lý"),
        ("staff", "Nhân viên"),
        ("driver", "Tài xế (chưa phân loại)"),
        ("driver_dumb_truck", "Tài xế xe ben"),
        ("driver_road_roller", "Tài xế xe lu"),
        ("driver_excavator", "Tài xế xe cuốc"),
        ("driver_construction", "Tài xế xe cơ giới khác"),
    )
    # Driver Information Fields
    full_name = models.CharField(max_length=255, verbose_name="Họ và tên", unique=True)
    hire_date = models.DateField(verbose_name="Ngày vào làm", default=timezone.now)
    identity_card = models.CharField(max_length=255, verbose_name="CCCD", default="")
    birth_year = models.DateField(verbose_name="Ngày sinh", default=timezone.now)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="active",
        verbose_name="Trạng thái",
    )
    position = models.CharField(
        max_length=50, choices=POSITION_CHOICES, default="staff", verbose_name="Vị trí"
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
    # Contact Information
    phone_number = models.CharField(
        max_length=15, verbose_name="Số điện thoại", default=""
    )
    address = models.CharField(max_length=255, verbose_name="Địa chỉ", default="")
    # Leave Information
    starting_leave_day_balance = models.FloatField(
        verbose_name="Bù trừ ngày phép",
        default=0.0,
        help_text="Số ngày phép khi bắt đầu dùng phần mềm",
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    def __str__(self):
        return f"{self.full_name} - {self.phone_number}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "full_name",
            "hire_date",
            "status",
            "position",
            "identity_card",
            "birth_year",
            "bank_name",
            "account_number",
            "account_holder_name",
            "phone_number",
            "address",
            "leave_day_balance",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class VehicleRevenueInputs(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "DL tính doanh thu theo loại xe cơ giới"

    class Meta:
        ordering = ["vehicle_type"]

    # Vehicle Information Fields
    vehicle_type = models.ForeignKey(
        VehicleType, on_delete=models.CASCADE, verbose_name="Loại xe"
    )
    # Revenue Information Fields
    revenue_day_price = models.IntegerField(
        verbose_name="Đơn giá doanh thu", default=0, validators=[MinValueValidator(0)]
    )

    # number of hours
    number_of_hours = models.IntegerField(
        verbose_name="Số giờ tính doanh thu",
        default=0,
        validators=[MinValueValidator(0)],
    )

    # number of liters of oil per hour
    oil_consumption_liters_per_hour = models.IntegerField(
        verbose_name="Số lít dầu 1 tiếng", default=0, validators=[MinValueValidator(0)]
    )

    # Resource Allocation Fields
    oil_consumption_per_hour = models.IntegerField(
        verbose_name="Định mức dầu 1 tiếng",
        default=0,
        validators=[MinValueValidator(0)],
    )
    lubricant_consumption = models.IntegerField(
        verbose_name="Định mức nhớt", default=0, validators=[MinValueValidator(0)]
    )
    insurance_fee = models.IntegerField(
        verbose_name="Định mức bảo hiểm", default=0, validators=[MinValueValidator(0)]
    )
    road_fee_inspection = models.IntegerField(
        verbose_name="Định mức sử dụng đường bộ/Đăng kiểm",
        default=0,
        validators=[MinValueValidator(0)],
    )
    tire_wear = models.IntegerField(
        verbose_name="Định mức hao mòn lốp xe",
        default=0,
        validators=[MinValueValidator(0)],
    )
    police_fee = models.IntegerField(
        verbose_name="Định mức CA", default=0, validators=[MinValueValidator(0)]
    )

    valid_from = models.DateField(
        verbose_name="Ngày bắt đầu áp dụng", default=timezone.now
    )

    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    def __str__(self):
        return f"{self.vehicle_type} - hiệu lực từ {self.valid_from}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "vehicle_type",
            "revenue_day_price",
            "number_of_hours",
            "oil_consumption_liters_per_hour",
            "oil_consumption_per_hour",
            "lubricant_consumption",
            "insurance_fee",
            "road_fee_inspection",
            "tire_wear",
            "police_fee",
            "valid_from",
            "note",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    # todo: thêm fields chạy ngày, chạy đêm, tabo ngày, mỗi cái có đơn giá => tính phí vận chuyể

    @classmethod
    def get_valid_record(self, vehicle_type, date):
        date = get_valid_date(date)
        return (
            VehicleRevenueInputs.objects.filter(
                vehicle_type=vehicle_type, valid_from__lte=date
            )
            .order_by("-valid_from")
            .first()
        )


class DriverSalaryInputs(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "DL tính lương xe cơ giới"

    class Meta:
        ordering = ["driver"]

    METHOD_CHOICES = (
        ("type_1", "Nghỉ chủ nhật và lễ, nếu đi làm được tính thêm lương (xe lu)"),
        ("type_2", "Không được nghỉ chủ nhật và lễ (xe cuốc)"),
    )

    driver = models.ForeignKey(
        StaffData,
        on_delete=models.CASCADE,
        verbose_name="Tài xế",
        limit_choices_to={"position__icontains": "driver"},
        null=True,
    )
    # Salary Fields
    basic_month_salary = models.PositiveIntegerField(
        verbose_name="Lương cơ bản tháng", default=0
    )
    sunday_month_salary_percentage = models.FloatField(
        verbose_name="Hệ số lương tháng ngày chủ nhật", default=0.0
    )
    holiday_month_salary_percentage = models.FloatField(
        verbose_name="Hệ số lương tháng ngày lễ", default=0.0
    )
    calculation_method = models.CharField(
        max_length=10,
        choices=METHOD_CHOICES,
        verbose_name="Phương pháp tính lương",
        default="type_1",
    )

    normal_hourly_salary = models.IntegerField(
        verbose_name="Lương theo giờ ngày thường", default=0
    )
    normal_overtime_hourly_salary = models.FloatField(
        verbose_name="Lương theo giờ tăng ca ngày thường", default=0
    )

    sunday_hourly_salary = models.IntegerField(
        verbose_name="Lương theo giờ chủ nhật", default=0
    )
    sunday_overtime_hourly_salary = models.FloatField(
        verbose_name="Lương theo giờ tăng ca chủ nhật", default=0
    )

    holiday_hourly_salary = models.IntegerField(
        verbose_name="Lương theo giờ ngày lễ", default=0
    )
    holiday_overtime_hourly_salary = models.FloatField(
        verbose_name="Lương theo giờ tăng ca ngày lễ", default=0
    )

    trip_salary = models.IntegerField(verbose_name="Lương theo chuyến", default=0)

    # Other Information
    fixed_allowance = models.PositiveIntegerField(
        verbose_name="Phụ cấp cố định", default=0
    )
    insurance_amount = models.PositiveIntegerField(
        verbose_name="Số tiền tham gia BHXH", default=0
    )

    valid_from = models.DateField(
        verbose_name="Ngày bắt đầu áp dụng", default=timezone.now
    )

    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    def __str__(self):
        return f"{self.driver} - hiệu lực từ {self.valid_from}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "driver",
            "valid_from",
            "basic_month_salary",
            "sunday_month_salary_percentage",
            "holiday_month_salary_percentage",
            "normal_hourly_salary",
            "normal_overtime_hourly_salary",
            "sunday_hourly_salary",
            "sunday_overtime_hourly_salary",
            "holiday_hourly_salary",
            "holiday_overtime_hourly_salary",
            "trip_salary",
            "fixed_allowance",
            "insurance_amount",
            "note",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class StaffSalaryInputs(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "DL tính lương nhân viên" # Đã sửa tên

    class Meta:
        ordering = ["staff", "-valid_from"] # Sửa ordering
        verbose_name = "Dữ liệu tính lương nhân viên"
        verbose_name_plural = "Dữ liệu tính lương nhân viên"

    staff = models.ForeignKey(
        StaffData,
        on_delete=models.CASCADE,
        verbose_name="Nhân viên",
        limit_choices_to={'position__in': ['manager', 'staff']},
        null=True,
        # blank=True # Cân nhắc thêm blank=True nếu bạn muốn form admin cho phép để trống
    )
    # Salary Fields
    basic_month_salary = models.PositiveIntegerField(
        verbose_name="Lương cơ bản tháng", default=0
    )
    # Hệ số lương cho ngày làm việc Chủ Nhật/Lễ (nếu nhân viên được tính thêm khi làm những ngày này)
    # Nếu không, có thể bỏ các trường này và chỉ dựa vào overtime_rate_multiplier
    sunday_work_day_multiplier = models.FloatField( # Đổi tên cho rõ nghĩa hơn
        verbose_name="Hệ số ngày làm việc Chủ Nhật", default=1.0, help_text="Mặc định 1.0 (100% lương ngày). Nếu làm CN được x2 lương ngày thì nhập 2.0"
    )
    holiday_work_day_multiplier = models.FloatField( # Đổi tên
        verbose_name="Hệ số ngày làm việc Lễ", default=1.0, help_text="Mặc định 1.0 (100% lương ngày). Nếu làm Lễ được x3 lương ngày thì nhập 3.0"
    )

    # Hệ số lương tăng ca (Overtime multipliers)
    overtime_normal_rate_multiplier = models.FloatField(
        verbose_name="Hệ số tăng ca ngày thường", default=1.5, help_text="Mặc định 1.5 (150%)"
    )
    overtime_sunday_rate_multiplier = models.FloatField(
        verbose_name="Hệ số tăng ca Chủ Nhật", default=2.0, help_text="Mặc định 2.0 (200%)"
    )
    overtime_holiday_rate_multiplier = models.FloatField(
        verbose_name="Hệ số tăng ca ngày Lễ", default=3.0, help_text="Mặc định 3.0 (300%)"
    )
    
    # Other Information
    fixed_allowance = models.PositiveIntegerField( # Các phụ cấp cố định khác không theo ngày
        verbose_name="Phụ cấp cố định", default=0
    )
    insurance_amount = models.PositiveIntegerField( # Mức lương đóng BHXH
        verbose_name="Mức lương đóng BHXH", default=0 
    )

    valid_from = models.DateField(
        verbose_name="Ngày bắt đầu áp dụng", default=timezone.now
    )

    note = models.TextField(
        verbose_name="Ghi chú", 
        default="", 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    def __str__(self):
        return f"{self.staff} - hiệu lực từ {self.valid_from}" # Sửa __str__

    @classmethod
    def get_display_fields(self):
        fields = [
            "staff",
            "valid_from",
            "basic_month_salary",
            "sunday_work_day_multiplier",
            "holiday_work_day_multiplier",
            "overtime_normal_rate_multiplier",
            "overtime_sunday_rate_multiplier",
            "overtime_holiday_rate_multiplier",
            "fixed_allowance",
            "insurance_amount",
            "note",
            "created_at",
        ]
        # Check if the field is in the model
        model_fields = [f.name for f in self._meta.get_fields()]
        return [field for field in fields if field in model_fields]

    @classmethod
    def get_valid_record(cls, staff_id, target_date):
        """
        Lấy bản ghi StaffSalaryInputs hợp lệ cho một nhân viên tại một ngày cụ thể.
        """
        # Chuyển đổi target_date sang đối tượng date nếu nó là string
        if isinstance(target_date, str):
            try:
                target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                target_date_obj = timezone.now().date() 
        elif isinstance(target_date, datetime):
            target_date_obj = target_date.date()
        elif isinstance(target_date, date):
            target_date_obj = target_date
        else:
            return None

        return cls.objects.filter(
            staff_id=staff_id,
            valid_from__lte=target_date_obj
        ).order_by('-valid_from').first()


class VehicleDetail(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Xe chi tiết"
    vehicle_type = models.ForeignKey(
        VehicleType, on_delete=models.SET_NULL, null=True, verbose_name="Loại xe"
    )
    license_plate = models.CharField(
        max_length=255, verbose_name="Biển kiểm soát", default="", unique=True
    )
    vehicle_name = models.CharField(
        max_length=255, verbose_name="Tên nhận dạng xe", default=""
    )
    gps_name = models.CharField(
        max_length=255, verbose_name="Tên trên định vị", default=""
    )
    vehicle_inspection_number = models.CharField(
        max_length=255, verbose_name="Số đăng kiểm"
    )
    vehicle_inspection_due_date = models.DateField(
        verbose_name="Thời hạn đăng kiểm", default=timezone.now, null=True
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    def __str__(self):
        return (
            f"{self.vehicle_name} - Biển số {self.license_plate} - GPS {self.gps_name}"
        )

    @classmethod
    def get_display_fields(self):
        fields = [
            "vehicle_type",
            "license_plate",
            "vehicle_name",
            "gps_name",
            "vehicle_inspection_number",
            "vehicle_inspection_due_date",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # create VehicleMaintenanceAnalysis
        if not VehicleMaintenanceAnalysis.objects.filter(vehicle=self).exists():
            VehicleMaintenanceAnalysis.objects.create(vehicle=self)


class VehicleMaintenanceAnalysis(BaseModel):
    allow_display = True
    vietnamese_name = "Thống kê sửa chữa"

    class Meta:
        ordering = ["vehicle"]

    vehicle = models.OneToOneField(
        VehicleDetail,
        on_delete=models.CASCADE,
        verbose_name="Xe",
    )
    maintenance_amount = models.IntegerField(
        verbose_name="Tổng chi phí sửa chữa",
        default=0,
        validators=[MinValueValidator(0)],
    )

    start_date = models.DateField(verbose_name="Từ ngày", default=timezone.now)
    end_date = models.DateField(verbose_name="Đến ngày", default=timezone.now)
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="Ngày tạo phiếu"
    )

    def __str__(self):
        return f"Thống kê sửa chữa xe {self.vehicle}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "vehicle",
            "maintenance_amount",
            "start_date",
            "end_date",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class DumbTruckPayRate(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "DL tính lương xe ben"
    xe = models.ForeignKey(
        VehicleDetail,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"vehicle_type__vehicle_type": "dump_truck"},
        verbose_name="Xe",
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
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    def __str__(self):
        return str(self.xe)

    @classmethod
    def get_display_fields(self):
        fields = [
            "xe",
            "chay_ngay",
            "chay_dem",
            "tanbo_ngay",
            "tanbo_dem",
            "chay_xa",
            "keo_xe",
            "keo_xe_ngay_le",
            "chay_ngay_le",
            "tanbo_ngay_le",
            "chay_xa_dem",
            "luong_co_ban",
            "tanbo_cat_bc",
            "tanbo_hh",
            "chay_thue_sr",
            "tanbo_cat_bc_dem",
            "tanbo_doi_3",
            "chay_nhua",
            "chay_nhua_dem",
            "keo_xe_dem",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class DumbTruckRevenueData(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "DL tính DT xe ben"
    # Choices for 'Loại chạy'
    LOAI_CHAY_CHOICES = [
        ("chay_ngay", "Chạy ngày"),
        ("chay_dem", "Chạy đêm"),
        ("chay_xa", "Chạy xa"),
        ("tanbo_ngay", "Tanbo ngày"),
        ("tanbo_dem", "Tanbo đêm"),
    ]

    # Choices for 'Cách tính'
    CACH_TINH_CHOICES = [
        ("tren_1_km", "Trên 1 km"),
        ("tren_chuyen", "Trên chuyến"),
    ]

    # Choices for 'Loại vật tư'
    LOAI_VAT_TU_CHOICES = [
        ("khong_vat_tu", "Không vật tư"),
        ("cat_dat_da", "Cát, đá, đất"),
        ("vat_tu_khac", "Vật tư khác"),
    ]

    # Choices for 'Mốc'
    MOC_CHOICES = [
        ("moc_1_20km", "Mốc 1 (0-20km)"),
        ("moc_2_35km", "Mốc 2 (0-35)"),
        ("moc_3_55km", "Mốc 3 (0-55)"),
    ]

    # Choices for 'Kích cỡ xe'
    KICH_CO_XE_CHOICES = [
        ("xe_nho", "Xe nhỏ"),
        ("xe_lon", "Xe lớn"),
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
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    def __str__(self):
        return f"{self.loai_chay} - {self.kich_co_xe}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "loai_chay",
            "cach_tinh",
            "loai_vat_tu",
            "moc",
            "kich_co_xe",
            "don_gia",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields


class NormalWorkingTime(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Thời gian làm việc xe cơ giới"

    # gotta get valid normal working time based on the valid date so that old data can be updated (from a button click manually)
    class Meta:
        ordering = ["-valid_from"]

    morning_start = models.TimeField(
        verbose_name="Bắt đầu ca sáng", default=time(7, 30)
    )
    morning_end = models.TimeField(
        verbose_name="Kết thúc ca sáng", default=time(11, 30)
    )
    afternoon_start = models.TimeField(
        verbose_name="Bắt đầu ca chiều", default=time(13, 0)
    )
    afternoon_end = models.TimeField(
        verbose_name="Kết thúc ca chiều", default=time(17, 0)
    )
    # Valid from
    valid_from = models.DateField(verbose_name="Ngày bắt đầu áp dụng")
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    def __str__(self):
        return f"{self.morning_start} đến {self.morning_end} - {self.afternoon_start} đến {self.afternoon_end} - hiệu lực từ {self.valid_from}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "morning_start",
            "morning_end",
            "afternoon_start",
            "afternoon_end",
            "valid_from",
            "note",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    @classmethod
    def get_valid_normal_working_time(self):
        # get the last valid working time
        normal_working_time = (
            NormalWorkingTime.objects.all().order_by("valid_from").last()
        )
        if normal_working_time:
            return (
                normal_working_time.morning_start,
                normal_working_time.morning_end,
                normal_working_time.afternoon_start,
                normal_working_time.afternoon_end,
            )
        else:
            # default working time
            morning_start = time(7, 30)
            morning_end = time(11, 30)
            afternoon_start = time(13, 0)
            afternoon_end = time(17, 0)
            return morning_start, morning_end, afternoon_start, afternoon_end

    def clean(self):
        errors = ""
        # if morning end is before morning start
        if self.morning_end < self.morning_start:
            errors += "- Bắt đầu ca sáng phải nhỏ hơn hoặc bằng kết thúc ca sáng.\n"
        # if afternoon end is before afternoon start
        if self.afternoon_end < self.afternoon_start:
            errors += "- Bắt đầu ca chiều phải nhỏ hơn hoặc bằng kết thúc ca chiều.\n"
        # if afternoon start is before morning end
        if self.afternoon_start < self.morning_end:
            errors += "- Bắt đầu ca chiều phải nhỏ hơn hoặc bằng kết thúc ca sáng.\n"
        if errors:
            raise ValidationError(errors)


class Holiday(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Ngày lễ"

    class Meta:
        ordering = ["-date"]

    date = models.DateField(verbose_name="Ngày lễ", unique=True)
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    def __str__(self):
        return f"{self.date} - {self.note}"

    @classmethod
    def get_display_fields(self):
        fields = ["date", "note", "created_at"]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    @classmethod
    def is_holiday(self, date):
        # check if the date is holiday
        holiday = Holiday.objects.filter(date=date).first()
        if holiday:
            return True
        else:
            return False


class VehicleOperationRecord(BaseModel):
    allow_display = True

    vietnamese_name = "DL HĐ xe công trình / ngày"
    SOURCE_CHOICES = [
        ("gps", "GPS"),
        ("manual", "Nhập tay"),
    ]
    TYPE_CHOICES = [
        ("plus", "Cộng"),
        ("minus", "Trừ"),
    ]

    class Meta:
        ordering = ["vehicle", "start_time"]

    vehicle = models.CharField(max_length=20, verbose_name="Xe")
    driver = models.ForeignKey(
        StaffData,
        on_delete=models.SET_NULL,
        verbose_name="Tài xế",
        limit_choices_to={"position__icontains": "driver"},
        null=True,
    )
    start_time = models.DateTimeField(
        verbose_name="Thời điểm mở máy", null=True, blank=True
    )
    end_time = models.DateTimeField(
        verbose_name="Thời điểm tắt máy", null=True, blank=True
    )
    duration_seconds = models.IntegerField(
        verbose_name="Thời gian hoạt động", default=0
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Địa điểm",
    )
    overtime = models.IntegerField(verbose_name="Thời gian tăng ca", default=0)
    normal_working_time = models.IntegerField(
        verbose_name="Thời gian làm hành chính", default=0
    )
    fuel_allowance = models.IntegerField(verbose_name="Phụ cấp xăng", default=0)
    image = models.ImageField(
        upload_to="images/vehicle_operations/",
        verbose_name="Hình ảnh",
        default="",
        null=True,
        blank=True,
    )
    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        verbose_name="Nguồn dữ liệu",
        default="gps",
    )
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)

    # add over time
    allow_overtime = models.BooleanField(
        verbose_name="Cho phép tính lương tăng ca", default=False
    )
    # add over time
    allow_revenue_overtime = models.BooleanField(
        verbose_name="Cho phép tính doanh thu tăng ca", default=True
    )

    def __str__(self):
        return f"{self.vehicle} - {self.start_time} - {self.end_time}"

    def delete(self, *args, **kwargs):
        print(
            ">>> [DELETE] VehicleOperationRecord: ",
            self.pk,
            self.vehicle,
            self.start_time,
        )
        # Save to a file
        with open("deleted_vehicle_operations.txt", "a") as f:
            text = f"VehicleOperationRecord: {self.pk} - {self.vehicle} - {self.start_time}\n"
            text += f"    - Vehicle: {self.vehicle}\n"
            text += f"    - Driver: {self.driver}\n"
            text += f"    - Location: {self.location}\n"
            text += f"    - Duration: {self.duration_seconds}\n"
            text += f"    - Source: {self.source}\n"
            text += f"    - Note: {self.note}\n"
            text += f"    - Image: {self.image}\n"
            text += f"    - Allow Overtime: {self.allow_overtime}\n"
            text += f"    - Allow Revenue Overtime: {self.allow_revenue_overtime}\n"
            text += f"    - Fuel Allowance: {self.fuel_allowance}\n"
            text += f"    - Overtime: {self.overtime}\n"
            text += f"    - Normal Working Time: {self.normal_working_time}\n"
            text += f"    - Start Time: {self.start_time}\n"
            text += f"    - End Time: {self.end_time}\n"

            text = text.strip() + "\n\n"
            f.write(text)
            # save all information

        if self.source == "manual":
            # allow delete
            super().delete(*args, **kwargs)

    @classmethod
    def get_display_fields(self):
        fields = [
            "vehicle",
            "start_time",
            "end_time",
            "duration_seconds",
            "source",
            "driver",
            "location",
            "normal_working_time",
            "overtime",
            "allow_overtime",
            "allow_revenue_overtime",
            "fuel_allowance",
            "image",
            "note",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def get_driver_choices(self):
        drivers = StaffData.objects.filter(
            position__icontains="driver", status__in=["active", "on_leave"]
        )
        # return a dict of choices with key id and name
        dict_drivers = [
            {"id": driver.id, "name": driver.full_name} for driver in drivers
        ]
        return dict_drivers

    def get_location_choices(self):
        locations = Location.objects.all()
        # return a dict of choices with key id and name
        dict_locations = [
            {"id": location.id, "name": location.name} for location in locations
        ]
        return dict_locations

    def calculate_working_time(self):
        if self.source != "gps":
            return self.normal_working_time, self.overtime

        start_time = self.start_time
        end_time = self.end_time
        # Define the working hours
        morning_start, morning_end, afternoon_start, afternoon_end = (
            NormalWorkingTime.get_valid_normal_working_time()
        )

        # get the set of seconds of the working hours
        the_order_of_second_of_morning_start = (
            morning_start.hour * 3600 + morning_start.minute * 60 + morning_start.second
        )
        the_order_of_second_of_morning_end = (
            morning_end.hour * 3600 + morning_end.minute * 60 + morning_end.second
        )
        the_order_of_second_of_afternoon_start = (
            afternoon_start.hour * 3600
            + afternoon_start.minute * 60
            + afternoon_start.second
        )
        the_order_of_second_of_afternoon_end = (
            afternoon_end.hour * 3600 + afternoon_end.minute * 60 + afternoon_end.second
        )

        # The set of all seconds working hours
        all_seconds_of_morning = set(
            range(
                the_order_of_second_of_morning_start, the_order_of_second_of_morning_end
            )
        )
        all_seconds_of_afternoon = set(
            range(
                the_order_of_second_of_afternoon_start,
                the_order_of_second_of_afternoon_end,
            )
        )
        all_seconds_of_working_hours = all_seconds_of_morning | all_seconds_of_afternoon

        # The set of all seconds from start_time to end_time
        the_order_of_second_of_start_time = (
            start_time.hour * 3600 + start_time.minute * 60 + start_time.second
        )
        the_order_of_second_of_end_time = (
            end_time.hour * 3600 + end_time.minute * 60 + end_time.second
        )
        all_seconds_from_start_to_end = set(
            range(the_order_of_second_of_start_time, the_order_of_second_of_end_time)
        )

        # The set of seconds that is overtime
        overtime = all_seconds_from_start_to_end - all_seconds_of_working_hours
        # count the number of seconds
        if overtime:
            normal_working_time = self.duration_seconds - len(overtime)
            self.normal_working_time = normal_working_time
            self.overtime = len(overtime)
            return normal_working_time, len(overtime)
        else:
            normal_working_time = self.duration_seconds
            self.normal_working_time = normal_working_time
            self.overtime = 0
            return normal_working_time, 0


class LiquidUnitPrice(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Đơn giá nhiên liệu/nhớt"
    TYPE_CHOICES = [
        ("diesel", "Dầu diesel (lít)"),
        ("gasoline", "Xăng (lít)"),
        ("lubricant_10", "Nhớt thủy lực (lít)"),
        ("lubricant_engine", "Nhớt máy xe cơ giới (lít)"),
        ("lubricant_engine_dumbtruck", "Nhớt máy xe ben (lít)"),
        ("lubricant_140_thick", "Nhớt 140 đặc (lít)"),
        ("lubricant_140", "Nhớt 140 lỏng (lít)"),
        ("grease", "Mỡ bò xe cơ giới (lít)"),
        ("grease_dumbtruck", "Mỡ bò xe ben (lít)"),
    ]
    liquid_type = models.CharField(
        max_length=100, choices=TYPE_CHOICES, verbose_name="Loại"
    )
    unit_price = models.IntegerField(
        verbose_name="Đơn giá", default=0, validators=[MinValueValidator(0)]
    )
    valid_from = models.DateField(
        verbose_name="Ngày bắt đầu áp dụng", default=timezone.now
    )
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    def __str__(self):
        return f"{self.liquid_type} - {self.unit_price} - {self.valid_from}"

    @classmethod
    def get_display_fields(self):
        fields = [
            "liquid_type",
            "unit_price",
            "unit",
            "valid_from",
            "note",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    @classmethod
    def get_unit_price(self, liquid_type, date):
        liquid_unit_price = (
            LiquidUnitPrice.objects.filter(
                liquid_type=liquid_type, valid_from__lte=date
            )
            .order_by("-valid_from")
            .first()
        )
        return liquid_unit_price

    def save(self):
        super().save()
        # recalculate all FillingRecord which liquid_type = liquid_type
        filling_records = FillingRecord.objects.filter(liquid_type=self.liquid_type)
        for filling_record in filling_records:
            filling_record.calculate_total_amount()
            filling_record.save()


class FillingRecord(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "LS đổ nhiên liệu/nhớt"

    class Meta:
        ordering = ["-fill_date"]

    TYPE_CHOICES = [
        ("diesel", "Dầu diesel (lít)"),
        ("gasoline", "Xăng (lít)"),
        ("lubricant_10", "Nhớt thủy lực (lít)"),
        ("lubricant_engine", "Nhớt máy xe cơ giới (lít)"),
        ("lubricant_engine_dumbtruck", "Nhớt máy xe ben (lít)"),
        ("lubricant_140_thick", "Nhớt 140 đặc (lít)"),
        ("lubricant_140", "Nhớt 140 lỏng (lít)"),
        ("grease", "Mỡ bò xe cơ giới (lít)"),
        ("grease_dumbtruck", "Mỡ bò xe ben (lít)"),
    ]
    liquid_type = models.CharField(
        max_length=100, choices=TYPE_CHOICES, verbose_name="Loại"
    )
    vehicle = models.ForeignKey(
        VehicleDetail,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Xe",
    )
    quantity = models.FloatField(verbose_name="Số lượng")
    total_amount = models.IntegerField(
        verbose_name="Thành tiền", default=0, validators=[MinValueValidator(0)]
    )
    fill_date = models.DateField(verbose_name="Ngày đổ", default=timezone.now)
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    def __str__(self):
        return f"{self.liquid_type} - {self.vehicle} - {self.quantity} - {self.total_amount} - {self.fill_date}"

    def save(self):
        self.calculate_total_amount()
        super().save()

    @classmethod
    def get_display_fields(self):
        fields = [
            "liquid_type",
            "vehicle",
            "quantity",
            "total_amount",
            "fill_date",
            "note",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def calculate_total_amount(self):
        # Get Unit Price
        unit_price = LiquidUnitPrice.get_unit_price(self.liquid_type, self.fill_date)
        if unit_price:
            self.total_amount = self.quantity * unit_price.unit_price
        else:
            self.total_amount = 0


class VehicleDepreciation(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Khấu hao xe"
    vehicle = models.ForeignKey(
        VehicleDetail,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Xe",
    )
    depreciation_amount = models.IntegerField(
        verbose_name="Khấu hao theo ngày", default=0, validators=[MinValueValidator(0)]
    )
    from_date = models.DateField(verbose_name="Ngày bắt đầu", default=timezone.now)
    to_date = models.DateField(verbose_name="Ngày kết thúc", default=timezone.now)
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    @classmethod
    def get_vehicle_depreciation(cls, vehicle, date):
        try:
            records = cls.objects.filter(
                vehicle=vehicle, from_date__lte=date, to_date__gte=date
            )
            # get the latest record
            records.order_by("-created_at")
            return records.first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_display_fields(self):
        fields = [
            "vehicle",
            "depreciation_amount",
            "from_date",
            "to_date",
            "note",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def __str__(self):
        return f"{self.vehicle} - {self.from_date} - {self.to_date}"


class VehicleBankInterest(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Lãi ngân hàng"
    vehicle = models.ForeignKey(
        VehicleDetail,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Xe",
    )
    interest_amount = models.IntegerField(
        verbose_name="Lãi suất theo ngày", default=0, validators=[MinValueValidator(0)]
    )
    from_date = models.DateField(verbose_name="Ngày bắt đầu", default=timezone.now)
    to_date = models.DateField(verbose_name="Ngày kết thúc", default=timezone.now)
    note = models.TextField(verbose_name="Ghi chú", default="", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    @classmethod
    def get_vehicle_bank_interest(cls, vehicle, date):
        try:
            records = cls.objects.filter(
                vehicle=vehicle, from_date__lte=date, to_date__gte=date
            )
            # get the latest record
            records.order_by("-created_at")
            return records.first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_display_fields(self):
        fields = [
            "vehicle",
            "interest_amount",
            "from_date",
            "to_date",
            "note",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def __str__(self):
        return f"{self.vehicle} - {self.from_date} - {self.to_date}"


class Announcement(BaseModel):
    allow_display = True
    excel_downloadable = True
    excel_uploadable = True
    vietnamese_name = "Thông báo"

    PRIORITY_CHOICES = [
        ("low", "Thấp"),
        ("medium", "Trung bình"),
        ("high", "Cao"),
        ("urgent", "Khẩn cấp"),
    ]

    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    content = models.TextField(verbose_name="Nội dung")
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="Người đăng"
    )
    publish_date = models.DateTimeField(verbose_name="Ngày đăng", default=timezone.now)
    attachment = models.FileField(
        upload_to="announcements/", verbose_name="Tệp đính kèm", null=True, blank=True
    )
    is_pinned = models.BooleanField(default=False, verbose_name="Ghim thông báo")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    class Meta:
        ordering = ["-is_pinned", "-publish_date"]

    def __str__(self):
        return str(self.title) + "- " + str(self.user) + " - " + str(self.publish_date)

    @classmethod
    def get_display_fields(self):
        fields = [
            "title",
            "content",
            "user",
            "publish_date",
            "expiry_date",
            "attachment",
            "is_pinned",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields

    def save(self):
        # Skip if user changed (keep first user)
        if self.pk:
            old_instance = Announcement.objects.get(pk=self.pk)
            if old_instance.user:
                self.user = old_instance.user
        super().save()


class ConstructionDriverSalaryDummy(BaseModel):
    allow_display = True
    vietnamese_name = "Bảng lương"


class ConstructionReportPLDummy(BaseModel):
    allow_display = True
    vietnamese_name = "Bảng P&L"


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class AttendanceRecord(BaseModel):
    allow_display = True
    excel_downloadable = False
    excel_uploadable = False
    vietnamese_name = "Chấm công"

    worker = models.ForeignKey(
        StaffData,
        on_delete=models.CASCADE,
        verbose_name="Nhân viên",
        related_name="attendance_records",
    )
    date = models.DateField(verbose_name="Ngày làm việc")

    WORK_DAY_CHOICES = [
        (Decimal("0.0"), "0.0"),
        (Decimal("0.5"), "0.5"),
        (Decimal("1.0"), "1.0"),
        (Decimal("1.5"), "1.5"),
        (Decimal("2.0"), "2.0"),
    ]
    work_day_count = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        choices=WORK_DAY_CHOICES,
        default=Decimal("1.0"),
        verbose_name="Công nhật",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("2.0")),
        ],
        help_text="Number of work days (e.g. 0.5, 1.0, 1.5, 2.0)",
    )

    ATTENDANCE_STATUS_CHOICES = [
        ("not_marked", "Chưa chấm công"),
        ("holiday_leave", "Nghỉ lễ"),
        ("hours_only", "Chỉ tính giờ"),
        ("holiday_leave", "Nghỉ lễ"),
        ("full_day", "Làm đủ ngày"),
        ("leave_day", "Nghỉ phép"),
        ("unpaid_leave", "Nghỉ không lương"),
        ("half_day_leave", "Nghỉ phép nửa ngày"),
        ("half_day_unpaid", "Nghỉ không lương nửa ngày"),
    ]
    attendance_status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS_CHOICES,
        default="not_marked",
        verbose_name="Trạng thái",
    )

    LEAVE_DAY_CHOICES = [
        (Decimal("0.0"), "0.0"),
        (Decimal("0.5"), "0.5"),
        (Decimal("1.0"), "1.0"),
    ]
    leave_day_count = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        choices=LEAVE_DAY_CHOICES,
        default=Decimal("0.0"),
        verbose_name="Ngày phép",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("1.0")),
        ],
        help_text="Số ngày phép được tính (0.0, 0.5, 1.0)",
    )
    
    LEAVE_COUNT_BALANCE_INCREASE_CHOICES = [
        (Decimal("0.0"), "0.0"),
        (Decimal("0.5"), "0.5"),
        (Decimal("1.0"), "1.0"),
        (Decimal("1.5"), "1.5"),
        (Decimal("2.0"), "2.0"),
        (Decimal("2.5"), "2.5"),
        (Decimal("3.0"), "3.0"),
    ]
    leave_count_balance_increase = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        choices=LEAVE_COUNT_BALANCE_INCREASE_CHOICES,
        default=Decimal("0.0"),
        verbose_name="Tăng ngày phép",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("3.0")),
        ],
        help_text="Số ngày phép được tăng thêm vào cuối tháng (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0)",
    )

    overtime_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Số giờ tăng ca",
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    note = models.TextField(
        blank=True,
        null=True,
        default="",
        verbose_name="Note",
        help_text="Ghi chú",
    )

    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

    def __str__(self):
        return f"{self.worker.full_name} - {self.date} - {self.attendance_status}"

    def save(self, *args, **kwargs):
        # Set work_day_count and leave_day_count based on attendance_status
        if self.attendance_status == "not_marked":
            self.work_day_count = Decimal("0.0")
            self.leave_day_count = Decimal("0.0")
            self.overtime_hours = Decimal("0.00")
        elif self.attendance_status == "full_day":
            self.work_day_count = Decimal("1.0")
            self.leave_day_count = Decimal("0.0")
        elif self.attendance_status == "leave_day":
            self.work_day_count = Decimal("1.0")
            self.leave_day_count = Decimal("1.0")
            self.overtime_hours = Decimal("0.00")
        elif self.attendance_status == "unpaid_leave":
            self.work_day_count = Decimal("0.0")
            self.leave_day_count = Decimal("0.0")
            self.overtime_hours = Decimal("0.00")
        elif self.attendance_status == "half_day_leave":
            self.work_day_count = Decimal("1.0")
            self.leave_day_count = Decimal("0.5")
            self.overtime_hours = Decimal("0.00")
        elif self.attendance_status == "half_day_unpaid":
            self.work_day_count = Decimal("0.5")
            self.leave_day_count = Decimal("0.0")
            self.overtime_hours = Decimal("0.00")
        elif self.attendance_status == "hours_only":
            self.work_day_count = Decimal("0.0")
            self.leave_day_count = Decimal("0.0")
        elif self.attendance_status == "holiday_leave":
            self.work_day_count = Decimal("1.0")
            self.leave_day_count = Decimal("0.0")
            self.overtime_hours = Decimal("0.00")

        super().save(*args, **kwargs)

    @classmethod
    def get_display_fields(self):
        fields = [
            "worker",
            "date",
            "attendance_status",
            "work_day_count",
            "leave_day_count",
            "leave_count_balance_increase",
            "overtime_hours",
            "note",
            "created_at",
        ]
        # Check if the field is in the model
        for field in fields:
            if not hasattr(self, field):
                fields.remove(field)
        return fields
