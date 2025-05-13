up.compiler('.display-calendar', function (modalForm) {
    const monthYear = document.getElementById('monthYear');
    const calendarDays = document.getElementById('calendarDays');
    const prevMonthBtn = document.getElementById('prevMonth');
    const nextMonthBtn = document.getElementById('nextMonth');
    const staffSelect = document.getElementById('staffSelect');
    const monthSelect = document.getElementById('monthSelect');

    const ATTENDANCE_STATUS_OPTIONS = [
        { value: "not_marked", text: "Chưa chấm công" },
        { value: "full_day", text: "Làm đủ ngày" },
        { value: "leave_day", text: "Nghỉ phép" },
        { value: "unpaid_leave", text: "Nghỉ không lương" },
        { value: "half_day_leave", text: "Làm nửa ngày, nghỉ phép nửa ngày" },
        { value: "half_day_unpaid", text: "Làm nửa ngày, nghỉ không lương nửa ngày" },
    ];

    const STATUS_COLORS = {
        "not_marked": "bg-gray-400",
        "full_day": "bg-green-500",
        "leave_day": "bg-yellow-500",
        "unpaid_leave": "bg-red-500",
        "half_day_leave": "bg-yellow-500", // Using same as leave_day
        "half_day_unpaid": "bg-orange-500"
    };

    let currentDate = new Date();
    let attendanceData = [];

    // Function to update month select input to match current date
    function updateMonthSelectInput() {
        const year = currentDate.getFullYear();
        const month = (currentDate.getMonth() + 1).toString().padStart(2, '0');
        monthSelect.value = `${year}-${month}`;
    }

    // Function to fetch attendance data from API
    async function fetchAttendanceData() {
        if (!staffSelect.value) {
            return [];
        }

        const year = currentDate.getFullYear();
        const month = currentDate.getMonth() + 1;
        const formattedMonth = `${year}-${month.toString().padStart(2, '0')}`;

        try {
            const response = await fetch(`/api/attendance-records/?staff_id=${staffSelect.value}&month=${formattedMonth}`);
            if (!response.ok) {
                throw new Error('Failed to fetch attendance data');
            }
            const data = await response.json();
            return data; // Return the whole object { records, holidays, salary_summary }
        } catch (error) {
            console.error('Error fetching attendance data:', error);
            return { records: [], holidays: {}, salary_summary: null }; // Return default structure on error
        }
    }

    // Function to fetch attendance summary data for all staff
    async function fetchAttendanceSummaryData() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth() + 1;
        const formattedMonth = `${year}-${month.toString().padStart(2, '0')}`;

        try {
            const response = await fetch(`/api/attendance-summary/?month=${formattedMonth}`);
            if (!response.ok) {
                throw new Error('Failed to fetch attendance summary data');
            }
            const data = await response.json();
            return data; // Return the whole object { summary, holidays }
        } catch (error) {
            console.error('Error fetching attendance summary data:', error);
            return { summary: {}, holidays: {} }; // Return default structure on error
        }
    }

    // Function to find attendance record for a specific date
    function findAttendanceRecord(date, year, month) {
        // Use provided year and month or fall back to currentDate
        const y = year !== undefined ? year : currentDate.getFullYear();
        const m = month !== undefined ? month + 1 : currentDate.getMonth() + 1;

        const dateStr = `${y}-${m.toString().padStart(2, '0')}-${date.toString().padStart(2, '0')}`;
        console.log('Looking for date:', dateStr, 'in', attendanceData.length, 'records');
        return attendanceData.find(record => record.date === dateStr);
    }

    async function renderCalendar(date) {
        calendarDays.innerHTML = '';
        const year = date.getFullYear();
        const month = date.getMonth();

        // Set month and year header
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        monthYear.textContent = monthNames[month] + ' ' + year;

        // Update month select input to match the calendar
        updateMonthSelectInput();

        // Check if we're viewing all staff or a specific staff member
        const isAllStaff = staffSelect.value === 'all';

        // Fetch appropriate data
        let summaryData = {};
        let holidaysData = {}; // To store holiday information
        let salarySummaryData = null; // To store salary summary for a single staff

        if (isAllStaff) {
            const apiResponse = await fetchAttendanceSummaryData();
            summaryData = apiResponse.summary || {};
            holidaysData = apiResponse.holidays || {};
        } else {
            const apiResponse = await fetchAttendanceData();
            console.log('API Response:', apiResponse); // Log the API response
            attendanceData = apiResponse.records || [];
            holidaysData = apiResponse.holidays || {};
            salarySummaryData = apiResponse.salary_summary || null; // Get salary summary
            console.log('Salary Summary Data:', salarySummaryData); // Log the salary summary data
        }

        // Get first day of the month
        const firstDay = new Date(year, month, 1);
        const startingDay = firstDay.getDay();

        // Get number of days in the month
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        // Fill in blank days before first day
        for (let i = 0; i < startingDay; i++) {
            const emptyCell = document.createElement('div');
            calendarDays.appendChild(emptyCell);
        }

        // Fill in days of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const dayCell = document.createElement('div');
            dayCell.classList.add('py-2', 'px-1', 'rounded', 'cursor-pointer', 'border', 'border-gray-300', 'dark:border-gray-600', 'min-h-[100px]', 'flex', 'flex-col');

            // Format date string
            const dateStr = `${year}-${(month + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
            const isHoliday = holidaysData && holidaysData[dateStr];

            // Container for day number and holiday name
            const dayLabelContainer = document.createElement('div');
            dayLabelContainer.classList.add('mb-1', 'text-center'); // Changed to text-center

            const dayNumberDiv = document.createElement('div');
            dayNumberDiv.textContent = day;
            // Make day number inline to allow holiday name next to it
            dayNumberDiv.classList.add('font-semibold', 'text-sm', 'inline');
            dayLabelContainer.appendChild(dayNumberDiv);

            if (isHoliday) {
                dayCell.classList.add('bg-purple-100', 'dark:bg-purple-600');
                const holidayNameSpan = document.createElement('span'); // Changed to span for inline display
                holidayNameSpan.classList.add('text-xs', 'text-purple-700', 'dark:text-purple-200', 'font-medium', 'leading-tight', 'ml-1'); // Removed mt-0.5, added ml-1
                holidayNameSpan.textContent = `(${holidaysData[dateStr]})`; // Added parentheses
                dayLabelContainer.appendChild(holidayNameSpan);
            }
            dayCell.appendChild(dayLabelContainer);

            // Highlight today & Hover effects
            const today = new Date();
            const isToday = day === today.getDate() && month === today.getMonth() && year === today.getFullYear();

            if (isToday) {
                if (isHoliday) {
                    dayNumberDiv.classList.add('ring-2', 'ring-blue-500', 'dark:ring-blue-300', 'rounded-full', 'px-1.5', 'py-0.5', 'inline-block'); // Added inline-block for ring to fit properly
                } else {
                    dayCell.classList.add('bg-blue-100', 'dark:bg-blue-800');
                }
            }

            // Simplified hover: if it's a holiday, it has purple bg, otherwise, it's normal/today.
            // Hover will apply on top of these.
            dayCell.classList.add('hover:bg-gray-200', 'dark:hover:bg-gray-700');

            if (isAllStaff) {
                // For "All Staff" view, open batch attendance modal
                dayCell.addEventListener('dblclick', () => {
                    openBatchAttendanceModal(dateStr, summaryData[dateStr]);
                });

                // Add summary data if available for this date
                if (summaryData && summaryData[dateStr]) {
                    const summary = summaryData[dateStr];

                    // Create summary info container
                    const summaryInfo = document.createElement('div');
                    summaryInfo.classList.add('text-xs', 'mt-1');

                    ATTENDANCE_STATUS_OPTIONS.forEach(statusOption => {
                        const countKey = `${statusOption.value}_count`; // e.g., full_day_count
                        const count = summary[countKey];

                        if (count > 0) {
                            const statusBadge = document.createElement('div');
                            const colorClass = STATUS_COLORS[statusOption.value] || 'bg-gray-500'; // Fallback color
                            statusBadge.className = `inline-block px-2 py-0.5 ${colorClass} text-white rounded-full text-xs font-semibold mb-1`; // py-0.5 for smaller badge
                            statusBadge.textContent = `${statusOption.text}: ${count}`;
                            summaryInfo.appendChild(statusBadge);
                            // Add a line break if you want each status on a new line, otherwise they will flow inline
                            summaryInfo.appendChild(document.createElement('br'));
                        }
                    });

                    dayCell.appendChild(summaryInfo);
                }
            } else {
                // For individual staff view, open individual attendance modal
                dayCell.addEventListener('dblclick', () => {
                    const existingRecord = findAttendanceRecord(day, year, month);
                    openAttendanceModal(dateStr, existingRecord);
                });

                // Add attendance data if available
                const record = findAttendanceRecord(day, year, month);
                if (record) {
                    // Background color for holidays is handled above.
                    // For individual attendance, we might want to show status colors more prominently.
                    // However, to avoid color clashing with holiday, we'll primarily use badges.

                    // Create attendance info container
                    const attendanceInfo = document.createElement('div');
                    attendanceInfo.classList.add('text-xs', 'mt-1');

                    // Add status badge
                    const statusBadge = document.createElement('div');
                    let badgeClass = 'inline-block px-2 py-1 rounded-full text-xs font-semibold mb-1 ';

                    switch (record.attendance_status) {
                        case 'full_day':
                            badgeClass += 'bg-green-500 text-white';
                            break;
                        case 'leave_day':
                            badgeClass += 'bg-yellow-500 text-white';
                            break;
                        case 'unpaid_leave':
                            badgeClass += 'bg-red-500 text-white';
                            break;
                        case 'half_day_leave':
                            badgeClass += 'bg-yellow-500 text-white';
                            break;
                        case 'half_day_unpaid':
                            badgeClass += 'bg-orange-500 text-white';
                            break;
                    }

                    statusBadge.className = badgeClass;

                    // Map status to Vietnamese
                    let statusText = '';
                    switch (record.attendance_status) {
                        case 'full_day':
                            statusText = ATTENDANCE_STATUS_OPTIONS.find(opt => opt.value === 'full_day').text;
                            break;
                        case 'leave_day':
                            statusText = ATTENDANCE_STATUS_OPTIONS.find(opt => opt.value === 'leave_day').text;
                            break;
                        case 'unpaid_leave':
                            statusText = ATTENDANCE_STATUS_OPTIONS.find(opt => opt.value === 'unpaid_leave').text;
                            break;
                        case 'half_day_leave':
                            statusText = ATTENDANCE_STATUS_OPTIONS.find(opt => opt.value === 'half_day_leave').text;
                            break;
                        case 'half_day_unpaid':
                            statusText = ATTENDANCE_STATUS_OPTIONS.find(opt => opt.value === 'half_day_unpaid').text;
                            break;
                    }
                    statusBadge.textContent = statusText;
                    attendanceInfo.appendChild(statusBadge);

                    // Add work day count with badge
                    const workDayBadge = document.createElement('div');
                    workDayBadge.className = 'inline-block px-2 py-1 bg-blue-500 text-white rounded-full text-xs font-semibold mt-1';
                    workDayBadge.textContent = `Công: ${record.work_day_count}`;
                    attendanceInfo.appendChild(workDayBadge);

                    // Add leave day count with badge if applicable
                    if (record.leave_day_count && record.leave_day_count > 0) {
                        const leaveDayBadge = document.createElement('div');
                        leaveDayBadge.className = 'inline-block px-2 py-1 bg-indigo-500 text-white rounded-full text-xs font-semibold ml-1 mt-1';
                        leaveDayBadge.textContent = `Phép: ${record.leave_day_count}`;
                        attendanceInfo.appendChild(leaveDayBadge);
                    }

                    // Add a line break
                    attendanceInfo.appendChild(document.createElement('br'));

                    // Add note if available
                    if (record.note) {
                        const noteDiv = document.createElement('div');
                        noteDiv.textContent = `Ghi chú: ${record.note}`;
                        noteDiv.className = 'text-gray-600 dark:text-gray-400 italic mt-1 text-xs overflow-hidden';
                        noteDiv.style.display = '-webkit-box';
                        noteDiv.style.webkitLineClamp = '2';
                        noteDiv.style.webkitBoxOrient = 'vertical';
                        attendanceInfo.appendChild(noteDiv);
                    }

                    dayCell.appendChild(attendanceInfo);
                }
            }

            calendarDays.appendChild(dayCell);
        }
        // Render salary summary table
        console.log('About to render salary summary with data:', salarySummaryData);
        renderSalarySummary(salarySummaryData);
    }

    prevMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar(currentDate);
        calculateSalary(); // Add this line to recalculate salary when changing to previous month
    });

    nextMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar(currentDate);
        calculateSalary(); // Add this line to recalculate salary when changing to next month
    });

    // Listen for staff selection changes
    staffSelect.addEventListener('change', () => {
        renderCalendar(currentDate);
        calculateSalary(); // Add this line to recalculate salary when staff changes
    });

    // Listen for month select input changes
    monthSelect.addEventListener('change', () => {
        if (monthSelect.value) {
            const [year, month] = monthSelect.value.split('-').map(Number);
            currentDate = new Date(year, month - 1, 1);
            renderCalendar(currentDate);
            calculateSalary(); // Add this line to recalculate salary when month changes
        }
    });

    // Initialize calendar with current date or from month select if available
    if (monthSelect.value) {
        const [year, month] = monthSelect.value.split('-').map(Number);
        currentDate = new Date(year, month - 1, 1);
    }
    renderCalendar(currentDate);

    // Add today button functionality
    const todayButton = document.getElementById('todayButton');
    if (todayButton) {
        todayButton.addEventListener('click', () => {
            currentDate = new Date();
            renderCalendar(currentDate);
            calculateSalary(); // Add this line to recalculate salary when going to today
        });
    }

    function renderSalarySummary(summary) {
        console.log('Rendering Salary Summary:', summary); // Log the summary data
        const salarySummaryContainer = document.getElementById('monthlySalarySummary');
        console.log('Salary Summary Container:', salarySummaryContainer); // Log the container element

        if (!salarySummaryContainer) {
            console.error('Salary Summary Container not found!');
            return;
        }

        salarySummaryContainer.innerHTML = ''; // Clear previous content

        if (summary && staffSelect.value !== 'all') {
            console.log('Staff selected, rendering summary'); // Log that we're rendering the summary
            const staffName = staffSelect.options[staffSelect.selectedIndex].text;

            // Check if summary has all required fields
            const requiredFields = ['num_days_in_month', 'sundays_in_month_count', 'total_leave_days',
                'total_unpaid_days', 'work_days_normal', 'work_days_sunday',
                'work_days_holiday', 'overtime_hours_normal', 'overtime_hours_sunday',
                'overtime_hours_holiday'];

            const missingFields = requiredFields.filter(field => summary[field] === undefined);
            if (missingFields.length > 0) {
                console.warn('Missing fields in summary:', missingFields);
                // Initialize missing fields with 0
                missingFields.forEach(field => {
                    summary[field] = 0;
                });
            }
            let summaryHtml = `
                <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-theme">
                    <h3 class="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Bảng tổng hợp công tháng cho: ${staffName}</h3>
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                <tr><td class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">Số ngày trong tháng:</td><td class="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">${summary.num_days_in_month}</td></tr>
                                <tr><td class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">Số ngày Chủ Nhật trong tháng:</td><td class="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">${summary.sundays_in_month_count}</td></tr>
                                <tr class="bg-gray-50 dark:bg-gray-750"><td colspan="2" class="px-4 py-1 text-xs font-semibold text-gray-500 dark:text-gray-400">CHI TIẾT CÔNG</td></tr>
                                <tr><td class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">Số ngày nghỉ phép:</td><td class="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">${summary.total_leave_days}</td></tr>
                                <tr><td class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">Số ngày nghỉ không lương:</td><td class="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">${summary.total_unpaid_days}</td></tr>
                                <tr><td class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">Số ngày công thường:</td><td class="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">${summary.work_days_normal}</td></tr>
                                <tr><td class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">Số ngày công Chủ Nhật:</td><td class="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">${summary.work_days_sunday}</td></tr>
                                <tr><td class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">Số ngày công ngày Lễ:</td><td class="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">${summary.work_days_holiday}</td></tr>
                                <tr class="bg-gray-50 dark:bg-gray-750"><td colspan="2" class="px-4 py-1 text-xs font-semibold text-gray-500 dark:text-gray-400">CHI TIẾT TĂNG CA</td></tr>
                                <tr><td class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">Số giờ tăng ca thường:</td><td class="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">${summary.overtime_hours_normal}</td></tr>
                                <tr><td class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">Số giờ tăng ca Chủ Nhật:</td><td class="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">${summary.overtime_hours_sunday}</td></tr>
                                <tr><td class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">Số giờ tăng ca Lễ:</td><td class="px-4 py-2 text-sm text-gray-900 dark:text-gray-100">${summary.overtime_hours_holiday}</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
            salarySummaryContainer.innerHTML = summaryHtml;
        } else {
            salarySummaryContainer.innerHTML = ''; // Clear if no specific staff selected or no summary data
        }
        adjustDisplayRecordsHeight();
    }

    // Individual Attendance Modal Functions
    const attendanceModal = document.getElementById('attendanceModal');
    const attendanceForm = document.getElementById('attendanceForm');
    const closeModalBtn = document.getElementById('closeModal');
    const cancelFormBtn = document.getElementById('cancelForm');
    const deleteRecordBtn = document.getElementById('deleteRecord');
    const recordIdInput = document.getElementById('recordId');
    const recordDateInput = document.getElementById('recordDate');
    const staffIdInput = document.getElementById('staffId');
    const staffNameInput = document.getElementById('staffName');
    const displayDateInput = document.getElementById('displayDate');
    const attendanceStatusSelect = document.getElementById('attendanceStatus');
    const overtimeHoursInput = document.getElementById('overtimeHours');
    const noteInput = document.getElementById('note');

    // Function to open the attendance modal
    function openAttendanceModal(dateStr, record = null) {
        // Format date for display (YYYY-MM-DD to DD/MM/YYYY)
        const [year, month, day] = dateStr.split('-');
        const formattedDate = `${day}/${month}/${year}`;

        // Get staff info
        const staffId = staffSelect.value;
        const staffName = staffSelect.options[staffSelect.selectedIndex].text;

        // Reset form
        attendanceForm.reset();

        // Set form values
        recordDateInput.value = dateStr;
        staffIdInput.value = staffId;
        staffNameInput.value = staffName;
        displayDateInput.value = formattedDate;
        overtimeHoursInput.value = '0'; // Default to 0 overtime hours

        // If editing existing record
        if (record) {
            recordIdInput.value = record.id;
            attendanceStatusSelect.value = record.attendance_status;
            overtimeHoursInput.value = (record.overtime_hours !== undefined && record.overtime_hours !== null) ? record.overtime_hours : '0';
            noteInput.value = record.note || '';
            deleteRecordBtn.classList.remove('hidden');
            console.log(record);

        } else {
            recordIdInput.value = '';
            attendanceStatusSelect.value = 'not_marked'; // Default to "Chưa chấm công"
            noteInput.value = '';
            deleteRecordBtn.classList.add('hidden');
        }

        // Show modal
        attendanceModal.classList.remove('hidden');
    }

    // Function to close the attendance modal
    function closeAttendanceModal() {
        attendanceModal.classList.add('hidden');
    }

    // Close modal events
    closeModalBtn.addEventListener('click', closeAttendanceModal);
    cancelFormBtn.addEventListener('click', closeAttendanceModal);

    // Batch Attendance Modal Functions
    const batchAttendanceModal = document.getElementById('batchAttendanceModal');
    const batchAttendanceForm = document.getElementById('batchAttendanceForm');
    const closeBatchModalBtn = document.getElementById('closeBatchModal');
    const cancelBatchFormBtn = document.getElementById('cancelBatchForm');
    const batchRecordDateInput = document.getElementById('batchRecordDate');
    const batchDisplayDateInput = document.getElementById('batchDisplayDate');
    const batchAttendanceTableBody = document.getElementById('batchAttendanceTableBody');
    const markAllPresentBtn = document.getElementById('markAllPresent');
    const markAllAbsentBtn = document.getElementById('markAllAbsent');
    const resetAllAttendanceBtn = document.getElementById('resetAllAttendance');

    // Function to fetch all staff members
    async function fetchAllStaff() {
        try {
            const response = await fetch('/api/staff/');
            if (!response.ok) {
                throw new Error('Failed to fetch staff data');
            }
            const data = await response.json();
            return data.staff || [];
        } catch (error) {
            console.error('Error fetching staff data:', error);
            return [];
        }
    }

    // Function to fetch attendance records for a specific date
    async function fetchAttendanceForDate(dateStr) {
        try {
            const response = await fetch(`/api/attendance-records/date/?date=${dateStr}`);
            if (!response.ok) {
                throw new Error('Failed to fetch attendance data for date');
            }
            const data = await response.json();
            return data.records || [];
        } catch (error) {
            console.error('Error fetching attendance data for date:', error);
            return [];
        }
    }

    // Function to open the batch attendance modal
    async function openBatchAttendanceModal(dateStr, summary = null) {
        // Format date for display (YYYY-MM-DD to DD/MM/YYYY)
        const [year, month, day] = dateStr.split('-');
        const formattedDate = `${day}/${month}/${year}`;

        // Set date values
        batchRecordDateInput.value = dateStr;
        batchDisplayDateInput.value = formattedDate;

        // Clear the table body
        batchAttendanceTableBody.innerHTML = '';

        // Fetch all staff members
        const allStaff = await fetchAllStaff();

        // Fetch attendance records for this date
        const dateAttendance = await fetchAttendanceForDate(dateStr);

        console.log('Attendance records for date:', dateAttendance);

        // Create a map of staff ID to attendance record
        const attendanceMap = {};
        dateAttendance.forEach(record => {
            attendanceMap[record.staff_id] = record;
        });

        // Add a row for each staff member
        allStaff.forEach((staff, index) => {
            const record = attendanceMap[staff.id] || null;

            const row = document.createElement('tr');
            row.className = index % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-700';

            // Staff name cell
            const nameCell = document.createElement('td');
            nameCell.className = 'px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100';
            nameCell.textContent = staff.full_name;

            // Hidden staff ID input
            const staffIdInput = document.createElement('input');
            staffIdInput.type = 'hidden';
            staffIdInput.name = `staff_id_${staff.id}`;
            staffIdInput.value = staff.id;
            nameCell.appendChild(staffIdInput);

            // Hidden record ID input (if exists)
            if (record) {
                const recordIdInput = document.createElement('input');
                recordIdInput.type = 'hidden';
                recordIdInput.name = `record_id_${staff.id}`;
                recordIdInput.value = record.id;
                nameCell.appendChild(recordIdInput);
            }

            // Status cell
            const statusCell = document.createElement('td');
            statusCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300';

            const statusSelect = document.createElement('select');
            statusSelect.className = 'form-input w-full';
            statusSelect.name = `attendance_status_${staff.id}`;

            ATTENDANCE_STATUS_OPTIONS.forEach(opt => {
                const option = document.createElement('option');
                option.value = opt.value;
                option.textContent = opt.text;
                statusSelect.appendChild(option);
            });
            // Set selected value if record exists
            if (record) {
                statusSelect.value = record.attendance_status;
            }

            statusCell.appendChild(statusSelect);

            // Note cell
            const noteCell = document.createElement('td');
            noteCell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300';

            const noteInput = document.createElement('input');
            noteInput.type = 'text';
            noteInput.className = 'form-input w-full';
            noteInput.name = `note_${staff.id}`;
            noteInput.placeholder = 'Ghi chú';

            // Set value if record exists
            if (record && record.note) {
                noteInput.value = record.note;
            }

            noteCell.appendChild(noteInput);

            // Create overtime hours cell
            const overtimeCell = document.createElement('td');
            overtimeCell.className = 'px-6 py-4 whitespace-nowrap';

            const overtimeInput = document.createElement('input');
            overtimeInput.type = 'number';
            overtimeInput.className = 'form-input w-full';
            overtimeInput.name = `overtime_hours_${staff.id}`;
            overtimeInput.placeholder = 'Số giờ tăng ca';
            overtimeInput.min = '0';
            overtimeInput.step = '0.1';

            // Set value if record exists
            if (record && record.overtime_hours !== undefined && record.overtime_hours !== null) {
                overtimeInput.value = record.overtime_hours;
            } else {
                overtimeInput.value = '0';
            }

            overtimeCell.appendChild(overtimeInput);

            // Add cells to row
            row.appendChild(nameCell);
            row.appendChild(statusCell);
            row.appendChild(overtimeCell);
            row.appendChild(noteCell);

            // Add row to table
            batchAttendanceTableBody.appendChild(row);
        });

        // Show modal
        batchAttendanceModal.classList.remove('hidden');
    }

    // Function to close the batch attendance modal
    function closeBatchAttendanceModal() {
        batchAttendanceModal.classList.add('hidden');
    }

    // Close batch modal events
    closeBatchModalBtn.addEventListener('click', closeBatchAttendanceModal);
    cancelBatchFormBtn.addEventListener('click', closeBatchAttendanceModal);

    // Mark all present button
    markAllPresentBtn.addEventListener('click', () => {
        const statusSelects = batchAttendanceTableBody.querySelectorAll('select[name^="attendance_status_"]');
        statusSelects.forEach(select => {
            select.value = 'full_day'; // Mark all as "Làm đủ ngày"
        });
    });

    // Mark all absent button
    markAllAbsentBtn.addEventListener('click', () => {
        const statusSelects = batchAttendanceTableBody.querySelectorAll('select[name^="attendance_status_"]');
        statusSelects.forEach(select => {
            select.value = 'unpaid_leave'; // Mark all as "Nghỉ không lương"
        });
    });

    // Reset all button
    resetAllAttendanceBtn.addEventListener('click', () => {
        const statusSelects = batchAttendanceTableBody.querySelectorAll('select[name^="attendance_status_"]');
        const overtimeInputs = batchAttendanceTableBody.querySelectorAll('input[name^="overtime_hours_"]');
        const noteInputs = batchAttendanceTableBody.querySelectorAll('input[name^="note_"]');

        statusSelects.forEach(select => {
            select.value = 'full_day'; // Reset to "Làm đủ ngày"
        });

        overtimeInputs.forEach(input => {
            input.value = '0'; // Reset overtime hours to 0
        });

        noteInputs.forEach(input => {
            input.value = '';
        });
    });

    // Handle individual form submission
    attendanceForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            record_id: recordIdInput.value || null,
            staff_id: staffIdInput.value,
            date: recordDateInput.value,
            attendance_status: attendanceStatusSelect.value,
            overtime_hours: overtimeHoursInput.value,
            note: noteInput.value
        };

        try {
            const response = await fetch('/api/attendance-records/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                // Success - refresh calendar
                closeAttendanceModal();
                renderCalendar(currentDate);

                // Show success message
                showMessage(data.message, 'success');
            } else {
                // Error
                showMessage(data.error, 'error');

                // If record already exists, update form with existing record
                if (response.status === 409 && data.record) {
                    recordIdInput.value = data.record.id;
                    attendanceStatusSelect.value = data.record.attendance_status;
                    noteInput.value = data.record.note || '';
                    deleteRecordBtn.classList.remove('hidden');
                }
            }
        } catch (error) {
            showMessage('An error occurred while saving the record', 'error');
            console.error('Error saving attendance record:', error);
        }
    });

    // Handle batch form submission
    batchAttendanceForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Collect all form data
        const formData = {
            date: batchRecordDateInput.value,
            records: []
        };

        // Get all staff rows
        const staffIds = Array.from(batchAttendanceTableBody.querySelectorAll('input[name^="staff_id_"]')).map(input => {
            return input.value;
        });

        // For each staff, collect their attendance data
        staffIds.forEach(staffId => {
            const recordIdInput = batchAttendanceTableBody.querySelector(`input[name="record_id_${staffId}"]`);
            const statusSelect = batchAttendanceTableBody.querySelector(`select[name="attendance_status_${staffId}"]`);
            const overtimeInput = batchAttendanceTableBody.querySelector(`input[name="overtime_hours_${staffId}"]`);
            const noteInput = batchAttendanceTableBody.querySelector(`input[name="note_${staffId}"]`);

            formData.records.push({
                record_id: recordIdInput ? recordIdInput.value : null,
                staff_id: staffId,
                attendance_status: statusSelect.value,
                overtime_hours: overtimeInput ? overtimeInput.value : '0',
                note: noteInput.value
            });
        });

        try {
            const response = await fetch('/api/attendance-records/batch-save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                // Success - refresh calendar and close modal
                closeBatchAttendanceModal();
                renderCalendar(currentDate);

                // Show success message
                showMessage(data.message, 'success');
            } else {
                // Error
                showMessage(data.error, 'error');
            }
        } catch (error) {
            showMessage('An error occurred while saving the records', 'error');
            console.error('Error saving batch attendance records:', error);
        }
    });

    // Handle delete button
    deleteRecordBtn.addEventListener('click', async () => {
        if (!recordIdInput.value) return;

        if (!confirm('Are you sure you want to delete this attendance record?')) {
            return;
        }

        try {
            const response = await fetch(`/api/attendance-records/delete/${recordIdInput.value}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });

            const data = await response.json();

            if (response.ok) {
                // Success - refresh calendar
                closeAttendanceModal();
                renderCalendar(currentDate);

                // Show success message
                showMessage(data.message, 'success');
            } else {
                // Error
                showMessage(data.error, 'error');
            }
        } catch (error) {
            showMessage('An error occurred while deleting the record', 'error');
            console.error('Error deleting attendance record:', error);
        }
    });

    // Helper function to get CSRF token
    function getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }

    // Helper function to show messages
    function showMessage(message, type = 'info') {
        const messageContainer = document.getElementById('message');
        if (!messageContainer) return;

        const alertClass = type === 'error' ? 'alert-danger' :
            type === 'success' ? 'alert-success' : 'alert-info';

        messageContainer.innerHTML = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;

        // Auto-hide after 5 seconds
        setTimeout(() => {
            const alert = messageContainer.querySelector('.alert');
            if (alert) {
                alert.classList.remove('show');
                setTimeout(() => {
                    messageContainer.innerHTML = '';
                }, 500);
            }
        }, 5000);
    }

    // Salary calculation functionality
    function initSalaryCalculation() {
        // Calculate salary automatically when the page loads
        calculateSalary();
    }

    // Calculate salary for the current month shown in the calendar
    function calculateSalary() {
        // Get the current month and year from the calendar
        const monthYearText = document.getElementById('monthYear').textContent;
        const [monthName, year] = monthYearText.split(' ');
        
        // Convert month name to month number (0-based)
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        const month = monthNames.indexOf(monthName);
        
        if (month === -1) {
            showSalaryError('Không thể xác định tháng hiện tại.');
            return;
        }
        
        // Create date objects for first and last day of the month
        const firstDay = new Date(parseInt(year), month, 1);
        const lastDay = new Date(parseInt(year), month + 1, 0);
        
        // Format dates as YYYY-MM-DD
        const formatDate = (date) => {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        };
        
        const startDate = formatDate(firstDay);
        const endDate = formatDate(lastDay);
        const staffId = staffSelect.value;
        
        // Only calculate salary for individual staff members, not for "all staff"
        if (staffId === 'all') {
            document.getElementById('salaryCalculationSection').classList.add('hidden');
            return;
        } else {
            document.getElementById('salaryCalculationSection').classList.remove('hidden');
        }
        
        // Show loading indicator
        document.getElementById('salary-results-container').classList.add('hidden');
        document.getElementById('salary-error').classList.add('hidden');
        document.getElementById('salary-no-data').classList.add('hidden');
        document.getElementById('salary-loading').classList.remove('hidden');
        
        // Build API URL
        let apiUrl = `/api/calculate-staff-salary/?start_date=${startDate}&end_date=${endDate}&staff_id=${staffId}`;
        
        // Make API request
        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                document.getElementById('salary-loading').classList.add('hidden');
                
                if (data.success) {
                    if (data.results && data.results.length > 0) {
                        displaySalaryResults(data.results);
                    } else {
                        document.getElementById('salary-no-data').classList.remove('hidden');
                    }
                } else {
                    showSalaryError(data.message || 'Có lỗi xảy ra khi tính lương.');
                }
            })
            .catch(error => {
                document.getElementById('salary-loading').classList.add('hidden');
                showSalaryError('Có lỗi xảy ra khi tính lương: ' + error.message);
                console.error('Error calculating salary:', error);
            });
    }

    // Display salary calculation results in the table
    function displaySalaryResults(results) {
        const tableBody = document.getElementById('salary-results-table');
        tableBody.innerHTML = '';
        
        // Format currency
        const formatCurrency = (amount) => {
            return new Intl.NumberFormat('vi-VN', { 
                style: 'currency', 
                currency: 'VND',
                maximumFractionDigits: 0
            }).format(amount);
        };
        
        // Add rows for each staff member
        results.forEach(staff => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-100 dark:hover:bg-gray-700';
            
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${staff.staff_id}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${staff.staff_name}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${staff.full_days}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${staff.half_days}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${staff.leave_days}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${staff.unpaid_leave_days}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${staff.normal_working_time}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${staff.overtime}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${formatCurrency(staff.base_salary)}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${formatCurrency(staff.daily_rate)}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${formatCurrency(staff.overtime_rate)}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${formatCurrency(staff.allowances)}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${formatCurrency(staff.normal_salary)}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">${formatCurrency(staff.overtime_salary)}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">${formatCurrency(staff.total_salary)}</td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Show the results container
        document.getElementById('salary-results-container').classList.remove('hidden');
    }

    // Show error message
    function showSalaryError(message) {
        const errorElement = document.getElementById('salary-error');
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');
    }

    // Export salary data to Excel
    function exportSalaryToExcel() {
        // Get the current month and year from the calendar
        const monthYearText = document.getElementById('monthYear').textContent;
        const [monthName, year] = monthYearText.split(' ');
        
        // Convert month name to month number (0-based)
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        const month = monthNames.indexOf(monthName);
        
        if (month === -1) {
            showSalaryError('Không thể xác định tháng hiện tại.');
            return;
        }
        
        // Create date objects for first and last day of the month
        const firstDay = new Date(parseInt(year), month, 1);
        const lastDay = new Date(parseInt(year), month + 1, 0);
        
        // Format dates as YYYY-MM-DD
        const formatDate = (date) => {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        };
        
        const startDate = formatDate(firstDay);
        const endDate = formatDate(lastDay);
        const staffId = staffSelect.value;
        
        // Build export URL
        let exportUrl = `/excel/export-staff-salary/?start_date=${startDate}&end_date=${endDate}`;
        if (staffId && staffId !== 'all') {
            exportUrl += `&staff_id=${staffId}`;
        }
        
        // Open the export URL in a new tab/window
        window.open(exportUrl, '_blank');
    }

    // Initialize salary calculation
    initSalaryCalculation();

    // Function to adjust display records height
    function adjustDisplayRecordsHeight() {
        const displayRecords = document.getElementById('display-records');
        if (displayRecords) {
            // Adjust height based on content
            const windowHeight = window.innerHeight;
            const navBarHeight = document.getElementById('tool-bar').offsetHeight;
            const footerHeight = 60; // Estimated footer height
            const padding = 40; // Additional padding
            
            displayRecords.style.maxHeight = `${windowHeight - navBarHeight - footerHeight - padding}px`;
        }
    }

    // Call adjust height on window resize
    window.addEventListener('resize', adjustDisplayRecordsHeight);
    
    // Initial adjustment
    adjustDisplayRecordsHeight();
});