from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, time
from decimal import Decimal
from .models.models import *
from django.db.models import Sum, Q
from .models.unclassified import Holiday

@login_required
@require_http_methods(["GET"])
def calculate_staff_salary(request):
    """
    Calculate salary for staff members based on attendance records within a date range.
    
    Query parameters:
    - start_date: Start date in YYYY-MM-DD format (required)
    - end_date: End date in YYYY-MM-DD format (required)
    - staff_id: Optional staff ID to calculate for a specific staff member
    """
    try:
        # Get date parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        staff_id = request.GET.get('staff_id')
        
        if not start_date_str or not end_date_str:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng cung cấp start_date và end_date'
            }, status=400)
            
        # Parse dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        # Get attendance records within date range
        records_query = AttendanceRecord.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            worker__isnull=False  # Changed from staff to worker
        )
        
        # Filter by staff if specified
        if staff_id:
            try:
                staff_id = int(staff_id)
                records_query = records_query.filter(worker=staff_id)  # Changed from staff to worker
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'staff_id không hợp lệ'
                }, status=400)
        
        # Get unique staff members
        staff_ids = records_query.values_list('worker', flat=True).distinct()  # Changed from staff to worker
        
        # Calculate salary for each staff member
        results = []
        for staff_id in staff_ids:
            staff = StaffData.objects.get(pk=staff_id)
            staff_records = records_query.filter(worker=staff_id)  # Changed from staff to worker
            
            # Calculate working times
            total_normal_working_time = 0
            total_overtime_normal = 0
            total_overtime_sunday = 0
            total_overtime_holiday = 0
            
            # Count attendance types
            full_day_count = staff_records.filter(attendance_status='full_day').count()
            half_day_leave_count = staff_records.filter(attendance_status='half_day_leave').count()
            half_day_unpaid_count = staff_records.filter(attendance_status='half_day_unpaid').count()
            leave_day_count = staff_records.filter(attendance_status='leave_day').count()
            unpaid_leave_count = staff_records.filter(attendance_status='unpaid_leave').count()
            not_marked_count = staff_records.filter(attendance_status='not_marked').count()
            
            # Standard working hours per day (8 hours = 28800 seconds)
            standard_day_seconds = 8 * 3600
            
            # Count working days by type
            normal_working_days = 0
            sunday_working_days = 0
            holiday_working_days = 0
            
            # Calculate total working time
            for record in staff_records:
                # Determine day type (normal, Sunday, or holiday)
                record_date = record.date
                is_sunday = record_date.weekday() == 6  # Sunday is 6 in Python's weekday
                is_holiday = Holiday.is_holiday(record_date)
                
                if record.attendance_status in ['full_day', 'hours_only']:
                    # Full day work
                    normal_working_time = standard_day_seconds
                    overtime = record.overtime_hours * 3600 if record.overtime_hours else 0
                    
                    # Count by day type
                    if is_holiday:
                        holiday_working_days += 1
                        total_overtime_holiday += overtime
                    elif is_sunday:
                        sunday_working_days += 1
                        total_overtime_sunday += overtime
                    else:
                        normal_working_days += 1
                        total_overtime_normal += overtime
                
                elif record.attendance_status in ['half_day_leave', 'half_day_unpaid']:
                    # Half day work (4 hours = 14400 seconds)
                    normal_working_time = standard_day_seconds / 2
                    overtime = 0
                    
                    # Count half days by type (as 0.5)
                    if is_holiday:
                        holiday_working_days += 0.5
                    elif is_sunday:
                        sunday_working_days += 0.5
                    else:
                        normal_working_days += 0.5
                
                else:
                    # Absent or leave
                    normal_working_time = 0
                    overtime = 0
                
                total_normal_working_time += normal_working_time
                
            # Total overtime (sum of all types)
            total_overtime = total_overtime_normal + total_overtime_sunday + total_overtime_holiday
            
            # Get salary configuration
            # Use the first record's date to determine the month
            staff_salary_inputs = None # Initialize
            if staff_records.exists():
                first_record_date = staff_records.first().date
                
                if first_record_date.month == 12:
                    end_date_of_month = datetime(first_record_date.year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    end_date_of_month = datetime(
                        first_record_date.year, first_record_date.month + 1, 1
                    ) - timedelta(days=1)
                
                staff_salary_inputs = StaffSalaryInputs.get_valid_record(
                    staff_id=staff_id,
                    target_date=end_date_of_month
                )
            
            # Calculate salary components
            base_salary = 0
            sunday_work_day_multiplier = 1.0
            holiday_work_day_multiplier = 1.0
            overtime_normal_rate_multiplier = 1.5
            overtime_sunday_rate_multiplier = 2.0
            overtime_holiday_rate_multiplier = 3.0
            fixed_allowance = 0
            insurance_amount = 0
            
            if staff_salary_inputs:
                base_salary = staff_salary_inputs.basic_month_salary or 0
                sunday_work_day_multiplier = staff_salary_inputs.sunday_work_day_multiplier or 1.0
                holiday_work_day_multiplier = staff_salary_inputs.holiday_work_day_multiplier or 1.0
                overtime_normal_rate_multiplier = staff_salary_inputs.overtime_normal_rate_multiplier or 1.5
                overtime_sunday_rate_multiplier = staff_salary_inputs.overtime_sunday_rate_multiplier or 2.0
                overtime_holiday_rate_multiplier = staff_salary_inputs.overtime_holiday_rate_multiplier or 3.0
                fixed_allowance = staff_salary_inputs.fixed_allowance or 0
                insurance_amount = staff_salary_inputs.insurance_amount or 0
            
            # Calculate actual normal and overtime hours
            actual_normal_hours = total_normal_working_time / 3600
            actual_overtime_normal_hours = total_overtime_normal / 3600
            actual_overtime_sunday_hours = total_overtime_sunday / 3600
            actual_overtime_holiday_hours = total_overtime_holiday / 3600

            # The variable `working_hours_per_day` is no longer needed for the new OT calculation
            # total_working_days = normal_working_days + sunday_working_days + holiday_working_days
            # working_hours_per_day = actual_normal_hours / total_working_days if total_working_days > 0 else 0


            # Calculate working days in the period
            total_days = (end_date - start_date).days + 1
            
            # Count days in month and Sundays for salary calculation
            days_in_month = 0
            sundays_in_month = 0
            
            if staff_records.exists():
                first_record_date = staff_records.first().date
                month = first_record_date.month
                year = first_record_date.year
                
                # Get the number of days in the month
                if month == 12:
                    last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    last_day = datetime(year, month + 1, 1) - timedelta(days=1)
                
                days_in_month = last_day.day
                
                # Count Sundays in the month
                current_date = datetime(year, month, 1).date()
                while current_date.month == month:
                    if current_date.weekday() == 6:  # Sunday
                        sundays_in_month += 1
                    current_date += timedelta(days=1)
            
            # Calculate daily rate
            working_days_in_month = days_in_month - sundays_in_month
            daily_rate = base_salary / working_days_in_month if working_days_in_month > 0 else 0
            daily_rate_decimal = Decimal(str(daily_rate))

            # Calculate salary components for normal work days, Sundays, and holidays (excluding overtime)
            normal_days_salary_component = daily_rate_decimal * Decimal(str(normal_working_days))
            sunday_days_salary_component = daily_rate_decimal * Decimal(str(sunday_working_days)) * Decimal(str(sunday_work_day_multiplier))
            holiday_days_salary_component = daily_rate_decimal * Decimal(str(holiday_working_days)) * Decimal(str(holiday_work_day_multiplier))

            # Calculate overtime salary
            # OT Salary = Actual_OT_Hours * (Daily_Rate / 8) * OT_Multiplier
            hourly_rate_for_ot_calc = daily_rate_decimal / Decimal('8.0') if daily_rate_decimal > 0 else Decimal('0.0')

            overtime_normal_salary = Decimal(str(actual_overtime_normal_hours)) * hourly_rate_for_ot_calc * Decimal(str(overtime_normal_rate_multiplier))
            overtime_sunday_salary = Decimal(str(actual_overtime_sunday_hours)) * hourly_rate_for_ot_calc * Decimal(str(overtime_sunday_rate_multiplier))
            overtime_holiday_salary = Decimal(str(actual_overtime_holiday_hours)) * hourly_rate_for_ot_calc * Decimal(str(overtime_holiday_rate_multiplier))
            total_overtime_salary = overtime_normal_salary + overtime_sunday_salary + overtime_holiday_salary
            
            # Calculate total salary
            total_salary = (
                normal_days_salary_component +
                sunday_days_salary_component +
                holiday_days_salary_component +
                total_overtime_salary +
                Decimal(str(fixed_allowance)) -
                Decimal(str(insurance_amount))
            )
            
            # Format times for display
            def format_time(seconds):
                hours = int(seconds // 3600)  # Use int() to ensure it's an integer
                minutes = int((seconds % 3600) // 60)  # Use int() to ensure it's an integer
                return f"{hours:02d}:{minutes:02d}:00"
            
            results.append({
                'staff_id': staff_id,
                'staff_name': staff.full_name,
                # Attendance counts
                'full_days': full_day_count,
                'half_days': half_day_leave_count + half_day_unpaid_count,
                'leave_days': leave_day_count,
                'unpaid_leave_days': unpaid_leave_count,
                'not_marked_days': not_marked_count,
                # Month info
                'num_days_in_month': days_in_month,
                'sundays_in_month_count': sundays_in_month,
                # Working days by type
                'work_days_normal': round(normal_working_days, 2),
                'work_days_sunday': round(sunday_working_days, 2),
                'work_days_holiday': round(holiday_working_days, 2),
                # Working times
                'normal_working_time': format_time(total_normal_working_time),
                'total_overtime': format_time(total_overtime),
                # Hours for calculations
                'normal_hours': round(actual_normal_hours, 2),
                'overtime_hours_normal': round(actual_overtime_normal_hours, 2),
                'overtime_hours_sunday': round(actual_overtime_sunday_hours, 2),
                'overtime_hours_holiday': round(actual_overtime_holiday_hours, 2),
                # Salary rates
                'base_salary': base_salary,
                'daily_rate': round(daily_rate, 2),
                'sunday_work_day_multiplier': sunday_work_day_multiplier,
                'holiday_work_day_multiplier': holiday_work_day_multiplier,
                'overtime_normal_rate_multiplier': overtime_normal_rate_multiplier,
                'overtime_sunday_rate_multiplier': overtime_sunday_rate_multiplier,
                'overtime_holiday_rate_multiplier': overtime_holiday_rate_multiplier,
                # Salary components
                'normal_days_salary_component': round(normal_days_salary_component, 2),
                'sunday_days_salary_component': round(sunday_days_salary_component, 2),
                'holiday_days_salary_component': round(holiday_days_salary_component, 2),
                'overtime_normal_salary': round(overtime_normal_salary, 2),
                'overtime_sunday_salary': round(overtime_sunday_salary, 2),
                'overtime_holiday_salary': round(overtime_holiday_salary, 2),
                'fixed_allowance': fixed_allowance,
                'insurance_amount': insurance_amount,
                # Totals
                'total_overtime_salary': round(total_overtime_salary, 2),
                'total_salary': round(total_salary, 2)
            })
        
        return JsonResponse({
            'success': True,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'results': results
        })
        
    except Exception as e:
        # Log the exception here if needed, e.g., logger.error(f"Error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=500)