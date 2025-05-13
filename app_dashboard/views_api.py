from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, time
from .models.models import *
from django.db.models import Sum, Q

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
            total_overtime = 0
            
            # Count attendance types
            full_day_count = staff_records.filter(attendance_status='full_day').count()  # Changed status to attendance_status
            half_day_leave_count = staff_records.filter(attendance_status='half_day_leave').count()  # Changed status to attendance_status
            half_day_unpaid_count = staff_records.filter(attendance_status='half_day_unpaid').count()  # Changed status to attendance_status
            leave_day_count = staff_records.filter(attendance_status='leave_day').count()  # Changed status to attendance_status
            unpaid_leave_count = staff_records.filter(attendance_status='unpaid_leave').count()  # Changed status to attendance_status
            not_marked_count = staff_records.filter(attendance_status='not_marked').count()  # Changed status to attendance_status
            
            # Standard working hours per day (8 hours = 28800 seconds)
            standard_day_seconds = 8 * 3600
            
            # Calculate total working time
            for record in staff_records:
                if record.attendance_status == 'full_day':  # Changed status to attendance_status
                    # Full day work
                    normal_working_time = standard_day_seconds
                    overtime = record.overtime_hours * 3600 if record.overtime_hours else 0
                
                elif record.attendance_status in ['half_day_leave', 'half_day_unpaid']:  # Changed status to attendance_status
                    # Half day work (4 hours = 14400 seconds)
                    normal_working_time = standard_day_seconds / 2
                    overtime = 0
                
                else:
                    # Absent or leave
                    normal_working_time = 0
                    overtime = 0
                
                total_normal_working_time += normal_working_time
                total_overtime += overtime
            
            # Get salary configuration
            # Use the first record's date to determine the month
            if staff_records.exists():
                first_record_date = staff_records.first().date
                start_date_of_month = datetime(first_record_date.year, first_record_date.month, 1)
                
                if first_record_date.month == 12:
                    end_date_of_month = datetime(first_record_date.year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date_of_month = datetime(
                        first_record_date.year, first_record_date.month + 1, 1
                    ) - timedelta(days=1)
                
                staff_salary_inputs = DriverSalaryInputs.objects.filter(
                    driver=staff_id, valid_from__lte=end_date_of_month
                ).order_by('-valid_from').first()
            else:
                staff_salary_inputs = None
            
            # Calculate salary components
            base_salary = 0
            overtime_rate = 0
            allowances = 0
            
            if staff_salary_inputs:
                base_salary = staff_salary_inputs.base_salary or 0
                overtime_rate = staff_salary_inputs.overtime_rate or 0
                allowances = staff_salary_inputs.allowances or 0
            
            # Calculate hours (convert seconds to hours)
            normal_hours = total_normal_working_time / 3600
            overtime_hours = total_overtime / 3600
            
            # Calculate working days in the period
            total_days = (end_date - start_date).days + 1
            working_days = sum(1 for day in (start_date + timedelta(days=x) for x in range(total_days)) 
                              if day.weekday() < 5)  # 0-4 are Monday to Friday
            
            # Calculate daily rate
            daily_rate = base_salary / working_days if working_days > 0 else 0
            
            # Calculate salary based on attendance
            normal_salary = daily_rate * (full_day_count + (half_day_leave_count * 0.5) + (half_day_unpaid_count * 0.5))
            overtime_salary = overtime_hours * overtime_rate
            
            total_salary = normal_salary + overtime_salary + allowances
            
            # Format times for display
            def format_time(seconds):
                hours = int(seconds // 3600)  # Use int() to ensure it's an integer
                minutes = int((seconds % 3600) // 60)  # Use int() to ensure it's an integer
                return f"{hours:02d}:{minutes:02d}:00"
            
            results.append({
                'staff_id': staff_id,
                'staff_name': staff.full_name,
                'full_days': full_day_count,
                'half_days': half_day_leave_count + half_day_unpaid_count,
                'leave_days': leave_day_count,
                'unpaid_leave_days': unpaid_leave_count,
                'not_marked_days': not_marked_count,
                'normal_working_time': format_time(total_normal_working_time),
                'overtime': format_time(total_overtime),
                'normal_hours': round(normal_hours, 2),
                'overtime_hours': round(overtime_hours, 2),
                'base_salary': base_salary,
                'daily_rate': round(daily_rate, 2),
                'overtime_rate': overtime_rate,
                'allowances': allowances,
                'normal_salary': round(normal_salary, 2),
                'overtime_salary': round(overtime_salary, 2),
                'total_salary': round(total_salary, 2)
            })
        
        return JsonResponse({
            'success': True,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=500)