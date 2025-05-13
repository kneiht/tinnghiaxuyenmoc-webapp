from django import template
from django.utils import timezone
from datetime import datetime, date, timedelta
import calendar
from decimal import Decimal

from ..models import *

register = template.Library()


@register.inclusion_tag("components/calculate_staff_salary.html")
def calculate_staff_salary(staff_id, year, month):
    """
    Calculate salary for non-driver staff members based on attendance data.

    Args:
        staff_id: The ID of the staff member
        year: The year for which to calculate the salary
        month: The month for which to calculate the salary

    Returns:
        Dictionary containing salary calculation details
    """
    # Get the staff member
    staff = StaffData.objects.filter(pk=staff_id).first()
    if not staff:
        return {
            "success": "false",
            "message": "Không tìm thấy nhân viên",
            "staff_name": "Unknown",
        }

    # Get the first and last day of the month
    first_day = date(int(year), int(month), 1)
    last_day = date(
        int(year), int(month), calendar.monthrange(int(year), int(month))[1]
    )

    # Get attendance records for the staff member in the specified month
    attendance_records = AttendanceRecord.objects.filter(
        worker=staff, date__range=(first_day, last_day)
    ).order_by("date")

    if not attendance_records:
        return {
            "success": "false",
            "message": "Không tìm thấy dữ liệu chấm công cho nhân viên này trong tháng đã chọn",
            "staff_name": staff.full_name,
        }

    # Get holidays for the month
    holidays_in_month = Holiday.objects.filter(
        date__year=int(year), date__month=int(month)
    )
    holidays_dict = {
        holiday.date.strftime("%Y-%m-%d"): holiday.note for holiday in holidays_in_month
    }

    # Calculate monthly salary summary
    days_in_month = calendar.monthrange(int(year), int(month))[1]

    # Count Sundays in the month
    sundays_in_month_count = sum(
        1
        for day in range(1, days_in_month + 1)
        if date(int(year), int(month), day).weekday() == 6
    )

    # Initialize counters
    total_leave_days = 0
    total_unpaid_days = 0
    work_days_normal = 0
    work_days_sunday = 0
    work_days_holiday = 0
    overtime_hours_normal = 0
    overtime_hours_sunday = 0
    overtime_hours_holiday = 0

    # Process each attendance record
    for record in attendance_records:
        date_str = record.date.strftime("%Y-%m-%d")
        is_sunday = record.date.weekday() == 6
        is_holiday = date_str in holidays_dict

        # Count leave days
        if record.attendance_status in ["leave_day", "half_day_leave"]:
            total_leave_days += float(record.leave_day_count)

        # Count unpaid leave days
        if record.attendance_status in ["unpaid_leave", "half_day_unpaid"]:
            total_unpaid_days += (
                1 if record.attendance_status == "unpaid_leave" else 0.5
            )

        # Count work days by type
        if float(record.work_day_count) > 0:
            if is_holiday:
                work_days_holiday += float(record.work_day_count)
            elif is_sunday:
                work_days_sunday += float(record.work_day_count)
            else:
                work_days_normal += float(record.work_day_count)

        # Count overtime hours by type
        if hasattr(record, "overtime_hours") and record.overtime_hours:
            overtime_hours = float(record.overtime_hours)
            if overtime_hours > 0:
                if is_holiday:
                    overtime_hours_holiday += overtime_hours
                elif is_sunday:
                    overtime_hours_sunday += overtime_hours
                else:
                    overtime_hours_normal += overtime_hours

    # Now calculate the salary based on the attendance data
    # We'll use a similar approach to the driver salary calculation

    # Define salary rates - these could be stored in a model in the future
    # For now, we'll use default values
    basic_month_salary = 5000000  # Default basic salary
    daily_rate = basic_month_salary / (days_in_month - sundays_in_month_count)
    sunday_rate_multiplier = 2.0  # Sunday work is paid double
    holiday_rate_multiplier = 3.0  # Holiday work is paid triple

    # Overtime rates
    normal_overtime_rate = 30000  # Per hour
    sunday_overtime_rate = 60000  # Per hour
    holiday_overtime_rate = 90000  # Per hour

    # Calculate salary components
    normal_days_salary = work_days_normal * daily_rate
    sunday_days_salary = work_days_sunday * daily_rate * sunday_rate_multiplier
    holiday_days_salary = work_days_holiday * daily_rate * holiday_rate_multiplier

    normal_overtime_salary = overtime_hours_normal * normal_overtime_rate
    sunday_overtime_salary = overtime_hours_sunday * sunday_overtime_rate
    holiday_overtime_salary = overtime_hours_holiday * holiday_overtime_rate

    # Calculate total salary
    total_work_days_salary = (
        normal_days_salary + sunday_days_salary + holiday_days_salary
    )
    total_overtime_salary = (
        normal_overtime_salary + sunday_overtime_salary + holiday_overtime_salary
    )
    total_salary = total_work_days_salary + total_overtime_salary

    # Prepare the data for the template
    salary_data = {
        "basic_month_salary": basic_month_salary,
        "daily_rate": daily_rate,
        "sunday_rate_multiplier": sunday_rate_multiplier,
        "holiday_rate_multiplier": holiday_rate_multiplier,
        "normal_overtime_rate": normal_overtime_rate,
        "sunday_overtime_rate": sunday_overtime_rate,
        "holiday_overtime_rate": holiday_overtime_rate,
        # Attendance summary
        "days_in_month": days_in_month,
        "sundays_in_month_count": sundays_in_month_count,
        "total_leave_days": total_leave_days,
        "total_unpaid_days": total_unpaid_days,
        "work_days_normal": work_days_normal,
        "work_days_sunday": work_days_sunday,
        "work_days_holiday": work_days_holiday,
        "overtime_hours_normal": overtime_hours_normal,
        "overtime_hours_sunday": overtime_hours_sunday,
        "overtime_hours_holiday": overtime_hours_holiday,
        # Salary components
        "normal_days_salary": normal_days_salary,
        "sunday_days_salary": sunday_days_salary,
        "holiday_days_salary": holiday_days_salary,
        "normal_overtime_salary": normal_overtime_salary,
        "sunday_overtime_salary": sunday_overtime_salary,
        "holiday_overtime_salary": holiday_overtime_salary,
        "total_work_days_salary": total_work_days_salary,
        "total_overtime_salary": total_overtime_salary,
        "total_salary": total_salary,
    }

    return {
        "success": "true",
        "message": "Tính toán lương thành công",
        "staff_name": staff.full_name,
        "data": salary_data,
    }
