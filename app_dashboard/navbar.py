from .models.models import *

NAV_ITEMS = {
    "page_home": {
        "page_name": "Trang chủ",
        "sub_pages": {
            "Announcement": "Thông báo",
            "User": User.get_vietnamese_name(),
            "Permission": Permission.get_vietnamese_name(),
            "ProjectUser": ProjectUser.get_vietnamese_name(),
        },
    },
    "page_projects": {
        "page_name": "Dự án",
        "sub_pages": {
            "Project": "Dự án",
            "SupplyProvider": "Nhà cung cấp vật tư",
            "SupplyBrand": "Thương hiệu vật tư",
            "BaseSupply": "Vật tư",
            "DetailSupply": "Vật tư chi tiết",
            "SupplyPaymentRecord": "LS thanh toán vật tư",
            "SubContractor": "Tổ đội/ nhà thầu phụ",
            "BaseSubJob": "Công việc của tổ đội/ nhà thầu phụ",
            "DetailSubJob": "Công việc chi tiết của tổ đội/ nhà thầu phụ",
            "SubJobPaymentRecord": "LS thanh toán công việc của tổ đội/ nhà thầu phụ",
            "OperationReceiver": "Bên thụ hưởng chi phí vận hành",
            "OperationPaymentRecord": "LS thanh toán phiếu đề xuất",
        },
    },
    "page_general_data": {
        "page_name": "Dữ liệu chung",
        "sub_pages": {
            "VehicleType": "DL loại xe",
            "VehicleRevenueInputs": "DL tính DT theo loại xe cơ giới",
            "VehicleDetail": "DL xe chi tiết",
            "StaffData": "DL nhân viên, tài xế phòng vận tải",
            "DriverSalaryInputs": "DL mức lương tài xế cơ giới",
            "DumbTruckPayRate": "DL mức lương tài xế xe ben",
            "DumbTruckRevenueData": "DL tính DT xe ben",
            "Location": "DL địa điểm",
            "NormalWorkingTime": "Thời gian làm việc xe cơ giới",
            "Holiday": "Ngày lễ",
        },
    },
    "page_transport_department": {
        "page_name": "Phòng vận tải",
        "sub_pages": {
            "LiquidUnitPrice": "Bảng đơn giá nhiên liệu/nhớt",
            "FillingRecord": "LS đổ nhiên liệu/nhớt",
            "PartProvider": "Nhà cung cấp phụ tùng",
            "RepairPart": "Danh mục phụ tùng",
            "PaymentRecord": "LS thanh toán",
            "VehicleMaintenance": "Phiếu sửa chữa",
            "VehicleMaintenanceAnalysis": "Thống kê sửa chữa",
            "VehicleDepreciation": "Khấu hao",
            "VehicleBankInterest": "Lãi ngân hàng",
            "VehicleOperationRecord": "DL HĐ xe cơ giới / ngày",
            "ConstructionDriverSalary": "Bảng lương tài xế cơ giới",
            "ConstructionReportPL": "Bảng BC P&L xe cơ giới",
        },
    },
    "page_attendance_calendar": {
        "page_name": "Văn phòng",
        "sub_pages": {
            "Attendance": "Chấm công",
        },
    },
}
