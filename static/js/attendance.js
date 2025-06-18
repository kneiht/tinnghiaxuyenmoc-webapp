up.compiler('.display-calendar', function (modalForm) {
    const monthYear = document.getElementById('monthYear');
    const calendarDays = document.getElementById('calendarDays');
    const prevMonthBtn = document.getElementById('prevMonth');
    const nextMonthBtn = document.getElementById('nextMonth');
    const staffSelect = document.getElementById('staffSelect');
    const monthSelect = document.getElementById('monthSelect');

    const ATTENDANCE_STATUS_OPTIONS = [
        { value: "not_marked", text: "Chưa chấm công" },
        { value: "holiday_leave", text: "Nghỉ lễ" },
        { value: "full_day", text: "Làm đủ ngày" },
        { value: "hours_only", text: "Chỉ tính giờ" }, // Trạng thái mới
        { value: "leave_day", text: "Nghỉ phép" },
        { value: "unpaid_leave", text: "Nghỉ không lương" },
        { value: "half_day_leave", text: "Nghỉ phép nửa ngày" },
        { value: "half_day_unpaid", text: "Nghỉ không lương nửa ngày" },
    ];

    const STATUS_COLORS = {
        "not_marked": "bg-gray-400",
        "holiday_leave": "bg-blue-500",
        "full_day": "bg-green-500",
        "hours_only": "bg-sky-500", // Màu cho trạng thái mới (ví dụ: xanh da trời)
        "leave_day": "bg-yellow-500",
        "unpaid_leave": "bg-red-500",
        "half_day_leave": "bg-yellow-500", // Using same as leave_day
        "half_day_unpaid": "bg-orange-500",
    };

    let currentDate = new Date();
    let attendanceData = [];
    let holidaysData = {}; // Make holidaysData accessible in openAttendanceModal

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
            console.log(data);
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
        // holidaysData is now a global variable within this up.compiler scope

        if (isAllStaff) {
            const apiResponse = await fetchAttendanceSummaryData();
            summaryData = apiResponse.summary || {};
            holidaysData = apiResponse.holidays || {};
        } else {
            const apiResponse = await fetchAttendanceData();
            attendanceData = apiResponse.records || [];
            holidaysData = apiResponse.holidays || {};
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

            const currentDateObjForLoop = new Date(year, month, day);
            const isCurrentDaySunday = currentDateObjForLoop.getDay() === 0; // 0 for Sunday

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
                    const statusOption = ATTENDANCE_STATUS_OPTIONS.find(opt => opt.value === record.attendance_status);
                    const statusText = statusOption ? statusOption.text : record.attendance_status; // Fallback to raw status if not found
                    const badgeColor = STATUS_COLORS[record.attendance_status] || 'bg-gray-500'; // Fallback color

                    statusBadge.className = `inline-block px-2 py-1 rounded-full text-xs font-semibold mb-1 ${badgeColor} text-white`;
                    statusBadge.textContent = statusText;
                    attendanceInfo.appendChild(statusBadge);

                    attendanceInfo.appendChild(document.createElement('br'));

                    // Add work day count with badge
                    const workDayBadge = document.createElement('div');
                    workDayBadge.className = 'inline-block px-2 py-1 bg-blue-500 text-white rounded-full text-xs font-semibold mt-1';

                    let prefix;
                    if (isHoliday) {
                        prefix = "Công lễ";
                    } else if (isCurrentDaySunday) {
                        prefix = "Công chủ nhật";
                    } else {
                        prefix = "Công thường";
                    }
                    let work_day_count_display = record.work_day_count;
                    if (isHoliday && record.attendance_status === 'holiday_leave' || record.attendance_status === 'hours_only') {
                        work_day_count_display = 1;
                        prefix = "Công thường";
                    }
                    workDayBadge.textContent = `${prefix}: ${work_day_count_display}`;
                    attendanceInfo.appendChild(workDayBadge);

                    // Add leave day count with badge if applicable
                    if (record.leave_day_count && parseFloat(record.leave_day_count) > 0) {
                        const leaveDayBadge = document.createElement('div');
                        leaveDayBadge.className = 'inline-block px-2 py-1 bg-indigo-500 text-white rounded-full text-xs font-semibold ml-1 mt-1';
                        attendanceInfo.appendChild(document.createElement('br'));
                        leaveDayBadge.textContent = `Phép trừ: ${record.leave_day_count}`;
                        attendanceInfo.appendChild(leaveDayBadge);
                    }
                    
                    // Add a line break
                    attendanceInfo.appendChild(document.createElement('br'));

                    let tc_prefix;
                    if (isHoliday) {
                        tc_prefix = "TC lễ";
                    } else if (isCurrentDaySunday) {
                        tc_prefix = "TC chủ nhật";
                    } else {
                        tc_prefix = "TC thường";
                    }

                    // Add overtime hours if available and greater than 0
                    if (record.overtime_hours && parseFloat(record.overtime_hours) > 0) {
                        const overtimeDiv = document.createElement('div');
                        overtimeDiv.className = 'inline-block px-2 py-1 bg-cyan-500 text-white rounded-full text-xs font-semibold mt-1';
                        overtimeDiv.textContent = `${tc_prefix}: ${record.overtime_hours}h`;
                        attendanceInfo.appendChild(overtimeDiv);
                    }
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
        adjustDisplayRecordsHeight(); // Ensure height is adjusted after calendar render
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
    calculateSalary();

    // Add today button functionality
    const todayButton = document.getElementById('todayButton');
    if (todayButton) {
        todayButton.addEventListener('click', () => {
            currentDate = new Date();
            renderCalendar(currentDate);
            calculateSalary(); // Add this line to recalculate salary when going to today
        });
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
    let attendanceStatusSelect = document.getElementById('attendanceStatus'); // Changed const to let
    const overtimeHoursInput = document.getElementById('overtimeHours');
    const leaveBalanceIncreaseContainer = document.getElementById('leaveBalanceIncreaseContainer');
    const leaveCountBalanceIncreaseSelect = document.getElementById('leaveCountBalanceIncrease');
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
        // First, remove any existing event listener to prevent duplicates if modal is reopened
        const newAttendanceStatusSelect = attendanceStatusSelect.cloneNode(true);
        attendanceStatusSelect.parentNode.replaceChild(newAttendanceStatusSelect, attendanceStatusSelect);
        attendanceStatusSelect = newAttendanceStatusSelect; // Re-assign to the new element

        // Also re-assign overtimeHoursInput if it's cloned or needs fresh reference, though typically not necessary unless form is complexly rebuilt
        // overtimeHoursInput = document.getElementById('overtimeHours'); // If needed

        // Check if it's the last day of the month to show leave_count_balance_increase field
        let dateObj = new Date(dateStr);
        const lastDayOfMonth = new Date(dateObj.getFullYear(), dateObj.getMonth() + 1, 0).getDate();
        const isLastDayOfMonth = parseInt(day) === lastDayOfMonth;
        
        if (isLastDayOfMonth) {
            leaveBalanceIncreaseContainer.classList.remove('hidden');
        } else {
            leaveBalanceIncreaseContainer.classList.add('hidden');
            leaveCountBalanceIncreaseSelect.value = '0.0'; // Reset to 0 if not last day
        }

        attendanceForm.reset();

        // Set form values
        recordDateInput.value = dateStr;
        staffIdInput.value = staffId;
        staffNameInput.value = staffName;
        displayDateInput.value = formattedDate;
        overtimeHoursInput.value = '0'; // Default to 0 overtime hours

        // Function to toggle overtime input based on status
        const toggleOvertimeInput = (status) => {
            if (status === 'full_day' || status === 'hours_only') {
                overtimeHoursInput.disabled = false;
            } else {
                overtimeHoursInput.disabled = true;
                overtimeHoursInput.value = '0'; // Reset overtime if disabled
            }
        };

        // If editing existing record
        if (record) {
            recordIdInput.value = record.id;
            attendanceStatusSelect.value = record.attendance_status;
            overtimeHoursInput.value = (record.overtime_hours !== undefined && record.overtime_hours !== null) ? record.overtime_hours : '0';
            
            // Set leave_count_balance_increase if it's available and it's the last day of the month
            if (isLastDayOfMonth && record.leave_count_balance_increase !== undefined) {
                leaveCountBalanceIncreaseSelect.value = record.leave_count_balance_increase.toString();
            } else {
                leaveCountBalanceIncreaseSelect.value = '0.0';
            }
            
            noteInput.value = record.note || '';
            deleteRecordBtn.classList.remove('hidden');
            toggleOvertimeInput(record.attendance_status); // Set initial state for overtime input

        } else {
            recordIdInput.value = '';
            attendanceStatusSelect.value = 'not_marked'; // Default to "Chưa chấm công"
            leaveCountBalanceIncreaseSelect.value = '0.0';
            noteInput.value = '';
            deleteRecordBtn.classList.add('hidden');
            toggleOvertimeInput('not_marked'); // Set initial state for overtime input
        }
        
        // Restrict status options if it's a holiday
        const isHoliday = holidaysData && holidaysData[dateStr];
        // Check if it's a Sunday
        dateObj = new Date(dateStr);
        const isSunday = dateObj.getDay() === 0; // 0 represents Sunday

        const allowedHolidayStatuses = ["holiday_leave", "full_day", "hours_only", "not_marked"];
        const allowedSundayStatuses = ["full_day", "hours_only", "not_marked"];
        const allowedWeekdayStatuses =  ["full_day", "hours_only", "leave_day", "unpaid_leave", "half_day_leave", "half_day_unpaid", "not_marked"];

        Array.from(attendanceStatusSelect.options).forEach(option => {
            if (isHoliday) { // Apply restriction if it's a holiday OR a Sunday
                if (allowedHolidayStatuses.includes(option.value)) {
                    option.style.display = ''; // Show allowed options
                } else {
                    option.style.display = 'none'; // Hide disallowed options
                }
            } else if (isSunday) { // Apply restriction if it's a Sunday
                if (allowedSundayStatuses.includes(option.value)) {
                    option.style.display = ''; // Show allowed options
                } else {
                    option.style.display = 'none'; // Hide disallowed options
                }
            }   else { // If not a holiday and not a Sunday (i.e., a normal weekday)
                if (allowedWeekdayStatuses.includes(option.value)) {
                    option.style.display = ''; // Show allowed options
                } else {
                    option.style.display = 'none'; // Hide disallowed options
                }
            }
        });
        // Ensure the selected value is visible, or reset to a default visible one
        // if (applyRestriction && attendanceStatusSelect.options[attendanceStatusSelect.selectedIndex].style.display === 'none') {
        //     attendanceStatusSelect.value = 'not_marked'; // Or another default visible status
        // }

        // Add event listener for status change to toggle overtime input
        attendanceStatusSelect.addEventListener('change', (event) => {
            toggleOvertimeInput(event.target.value);
        });

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
    const leaveBalanceIncreaseHeader = document.getElementById('leaveBalanceIncreaseHeader');

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
    async function openBatchAttendanceModal(dateStr, summary = null) { // holidaysData is globally available
        // Format date for display (YYYY-MM-DD to DD/MM/YYYY)
        const [year, month, day] = dateStr.split('-');
        const formattedDate = `${day}/${month}/${year}`;

        // Set date values
        batchRecordDateInput.value = dateStr;
        batchDisplayDateInput.value = formattedDate;

        // Check if it's the last day of the month to show leave_count_balance_increase field
        const dateObj2 = new Date(dateStr);
        const lastDayOfMonth = new Date(dateObj2.getFullYear(), dateObj2.getMonth() + 1, 0).getDate();
        const isLastDayOfMonth = parseInt(day) === lastDayOfMonth;
        
        if (isLastDayOfMonth) {
            leaveBalanceIncreaseHeader.classList.remove('hidden');
        } else {
            leaveBalanceIncreaseHeader.classList.add('hidden');
        }

        // Clear the table body
        batchAttendanceTableBody.innerHTML = '';

        // Fetch all staff members
        const allStaff = await fetchAllStaff();

        // Fetch attendance records for this date
        const dateAttendance = await fetchAttendanceForDate(dateStr);

        // Create a map of staff ID to attendance record
        const attendanceMap = {};
        dateAttendance.forEach(record => {
            attendanceMap[record.staff_id] = record;
        });

        // Determine if restrictions apply (Holiday or Sunday)
        const isHoliday = holidaysData && holidaysData[dateStr];
        const dateObj3 = new Date(dateStr);
        const isSunday = dateObj3.getDay() === 0;
        const allowedHolidayStatuses = ["holiday_leave", "full_day", "hours_only", "not_marked"];
        const allowedSundayStatuses = ["full_day", "hours_only", "not_marked"];
        const allowedWeekdayStatuses =  ["full_day", "hours_only", "leave_day", "unpaid_leave", "half_day_leave", "half_day_unpaid", "not_marked"];

        

        // Function to toggle overtime input based on status for a specific row
        const toggleBatchOvertimeInput = (statusSelectElement, overtimeInputElement) => {
            if (statusSelectElement.value === 'full_day' || statusSelectElement.value === 'hours_only') {
                overtimeInputElement.disabled = false;
            } else {
                overtimeInputElement.disabled = true;
                overtimeInputElement.value = '0';
            }
        };

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
            statusSelect.className = 'form-input w-full no-new-select';
            statusSelect.name = `attendance_status_${staff.id}`;

            ATTENDANCE_STATUS_OPTIONS.forEach(opt => {
                if (isHoliday) { // Apply restriction if it's a holiday OR a Sunday
                    if (allowedHolidayStatuses.includes(opt.value)) {
                        const option = document.createElement('option');
                        option.value = opt.value;
                        option.textContent = opt.text;
                        statusSelect.appendChild(option);
                    }
                } else if (isSunday) { // Apply restriction if it's a Sunday
                    if (allowedSundayStatuses.includes(opt.value)) {
                        const option = document.createElement('option');
                        option.value = opt.value;
                        option.textContent = opt.text;
                        statusSelect.appendChild(option);
                    }
                }   else { // If not a holiday and not a Sunday (i.e., a normal weekday)
                    if (allowedWeekdayStatuses.includes(opt.value)) {
                        const option = document.createElement('option');
                        option.value = opt.value;
                        option.textContent = opt.text;
                        statusSelect.appendChild(option);
                    }
                }
            });
            // Set selected value if record exists
            if (record) {
                statusSelect.value = record.attendance_status;
            } else {
                // If new record and restrictions apply, set to a default allowed status
                if (isHoliday || isSunday) {
                    statusSelect.value = 'not_marked';
                }
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
            }
            overtimeCell.appendChild(overtimeInput);

            // Initial state for overtime input
            toggleBatchOvertimeInput(statusSelect, overtimeInput);

            // Add event listener for status change to toggle overtime input for this row
            statusSelect.addEventListener('change', () => {
                toggleBatchOvertimeInput(statusSelect, overtimeInput);
            });
             // Ensure the selected value is visible, or reset to a default visible one
            // if (applyRestriction && statusSelect.options[statusSelect.selectedIndex] && statusSelect.options[statusSelect.selectedIndex].style.display === 'none') {
            //     statusSelect.value = 'not_marked'; // Or another default visible status
            // }
            // Create leave balance increase cell if it's the last day of the month
            if (isLastDayOfMonth) {
                const leaveBalanceCell = document.createElement('td');
                leaveBalanceCell.className = 'px-6 py-4 whitespace-nowrap';
                
                const leaveBalanceSelect = document.createElement('select');
                leaveBalanceSelect.className = 'form-input w-full no-new-select';
                leaveBalanceSelect.name = `leave_count_balance_increase_${staff.id}`;
                
                // Add options for leave balance increase
                [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0].forEach(value => {
                    const option = document.createElement('option');
                    option.value = value.toFixed(1);
                    option.textContent = value.toFixed(1);
                    leaveBalanceSelect.appendChild(option);
                });
                
                // Set value if record exists
                if (record && record.leave_count_balance_increase !== undefined) {
                    leaveBalanceSelect.value = record.leave_count_balance_increase.toFixed(1);
                }
                
                leaveBalanceCell.appendChild(leaveBalanceSelect);
                
                // Add cells to row
                row.appendChild(nameCell);
                row.appendChild(statusCell);
                row.appendChild(overtimeCell);
                row.appendChild(leaveBalanceCell);
                row.appendChild(noteCell);
            } else {
                // Add cells to row without leave balance increase
                row.appendChild(nameCell);
                row.appendChild(statusCell);
                row.appendChild(overtimeCell);
                row.appendChild(noteCell);
            }

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


    // Handle individual form submission
    attendanceForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const currentStatus = attendanceStatusSelect.value;
        const currentRecordId = recordIdInput.value;

        if (currentStatus === 'not_marked') {
            if (currentRecordId) { // If there's an existing record, delete it
                try {
                    const response = await fetch(`/api/attendance-records/delete/${currentRecordId}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': getCsrfToken()
                        }
                    });
                    const data = await response.json();
                    if (response.ok) {
                        closeAttendanceModal();
                        renderCalendar(currentDate);
                        calculateSalary();
                        
                        showMessage(data.message || 'Đã xóa chấm công.', 'success');
                    } else {
                        showMessage(data.error || 'Lỗi khi xóa chấm công.', 'error');
                    }
                } catch (error) {
                    showMessage('Lỗi khi xóa chấm công: ' + error.message, 'error');
                    console.error('Error deleting attendance record:', error);
                }
            } else { // No existing record, and "not_marked" is selected - just close
                closeAttendanceModal();
            }
            return; // Stop further execution
        }

        // Proceed with saving if status is not 'not_marked'
        const formData = {
            record_id: currentRecordId || null,
            staff_id: staffIdInput.value,
            date: recordDateInput.value,
            attendance_status: currentStatus,
            overtime_hours: overtimeHoursInput.value,
            note: noteInput.value
        };
        
        // Check if it's the last day of the month to include leave_count_balance_increase
        const dateStr = recordDateInput.value;
        const [year, month, day] = dateStr.split('-');
        const dateObj = new Date(dateStr);
        const lastDayOfMonth = new Date(dateObj.getFullYear(), dateObj.getMonth() + 1, 0).getDate();
        const isLastDayOfMonth = parseInt(day) === lastDayOfMonth;
        
        if (isLastDayOfMonth) {
            formData.leave_count_balance_increase = leaveCountBalanceIncreaseSelect.value;
        }

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
                calculateSalary();


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
            
            // Only add to records if status is not "not_marked" OR 
            // if it is "not_marked" but an existing record_id needs to be deleted (backend should handle this).
            // If status is "not_marked" for a new entry (no recordIdInput), we can skip it.
            // However, to allow deletion via "not_marked", we send it if recordIdInput exists.
            if (statusSelect.value !== 'not_marked' || (recordIdInput && recordIdInput.value)) {
                formData.records.push({
                    record_id: recordIdInput ? recordIdInput.value : null,
                    staff_id: staffId,
                    attendance_status: statusSelect.value,
                    overtime_hours: overtimeInput && !overtimeInput.disabled ? overtimeInput.value : '0',
                    note: noteInput.value
                });
            }
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
                calculateSalary();

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
                calculateSalary();

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

    // Display salary calculation results as cards
    function displaySalaryResults(results) {
        const cardsContainer = document.getElementById('salary-results-cards');
        cardsContainer.innerHTML = '';
        
        // Format currency
        const formatCurrency = (amount) => {
            return new Intl.NumberFormat('vi-VN', { 
                style: 'currency', 
                currency: 'VND',
                maximumFractionDigits: 0
            }).format(amount);
        };
        
        // Add cards for each staff member
        results.forEach(staff => {
            const card = document.createElement('div');
            card.className = 'bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden border border-gray-200 dark:border-gray-700';
            
            // Create card header with staff info
            const cardHeader = document.createElement('div');
            cardHeader.className = 'bg-gradient-to-r from-blue-500 to-indigo-600 p-4 text-white';
            cardHeader.innerHTML = `
                <div class="flex justify-between items-center">
                    <div>
                        <h3 class="text-lg font-bold">${staff.staff_name}</h3>
                        <p class="text-sm opacity-80">Mã NV: ${staff.staff_id}</p>
                    </div>
                    <div class="text-right">
                        <p class="text-2xl font-bold">${formatCurrency(staff.total_salary)}</p>
                        <p class="text-sm opacity-80">Tổng lương</p>
                    </div>
                </div>
            `;
            
            // Create card body with attendance details
            const attendanceSection = document.createElement('div');
            attendanceSection.className = 'p-4 border-b border-gray-200 dark:border-gray-700';

            let monthInfoHtml = '';
            if (staff.num_days_in_month !== undefined && staff.sundays_in_month_count !== undefined) {
                monthInfoHtml = `
                <div class="mb-3 text-sm text-gray-700 dark:text-gray-300">
                    <span>Tháng có <strong>${staff.num_days_in_month}</strong> ngày (trong đó có <strong>${staff.sundays_in_month_count}</strong> ngày Chủ Nhật)</span>
                </div>`;
            }

            // Determine if detailed work days are available
            const hasDetailedWorkDays = staff.work_days_normal !== undefined || staff.work_days_sunday !== undefined || staff.work_days_holiday !== undefined;

            let workDaysDetailHtml = `
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    <div class="bg-green-50 dark:bg-green-900/20 rounded p-2 text-center">
                        <span class="block text-xs text-gray-500 dark:text-gray-400">Công ngày thường</span>
                        <span class="block text-lg font-semibold text-gray-900 dark:text-gray-100">${staff.work_days_normal !== undefined ? staff.work_days_normal : (hasDetailedWorkDays ? 0 : (staff.full_days || 0))}</span>
                    </div>
                    ${staff.work_days_sunday !== undefined ? `
                    <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded p-2 text-center">
                        <span class="block text-xs text-gray-500 dark:text-gray-400">Công Chủ Nhật (hệ số: ${staff.sunday_work_day_multiplier})</span>
                        <span class="block text-lg font-semibold text-gray-900 dark:text-gray-100">${staff.work_days_sunday}</span>
                    </div>` : (hasDetailedWorkDays ? `<div class="bg-indigo-50 dark:bg-indigo-900/20 rounded p-2 text-center"><span class="block text-xs text-gray-500 dark:text-gray-400">Công Chủ Nhật</span><span class="block text-lg font-semibold text-gray-900 dark:text-gray-100">0</span></div>` : '')}
                    ${staff.work_days_holiday !== undefined ? `
                    <div class="bg-purple-50 dark:bg-purple-900/20 rounded p-2 text-center">
                        <span class="block text-xs text-gray-500 dark:text-gray-400">Công ngày Lễ (hệ số: ${staff.holiday_work_day_multiplier})</span>
                        <span class="block text-lg font-semibold text-gray-900 dark:text-gray-100">${staff.work_days_holiday}</span>
                    </div>` : (hasDetailedWorkDays ? `<div class="bg-purple-50 dark:bg-purple-900/20 rounded p-2 text-center"><span class="block text-xs text-gray-500 dark:text-gray-400">Công ngày Lễ</span><span class="block text-lg font-semibold text-gray-900 dark:text-gray-100">0</span></div>` : '')}
                    ${ staff.half_days !== undefined ? `
                    <div class="bg-blue-50 dark:bg-blue-900/20 rounded p-2 text-center">
                        <span class="block text-xs text-gray-500 dark:text-gray-400">Ngày phép tăng thêm</span>
                        <span class="block text-lg font-semibold text-gray-900 dark:text-gray-100">${staff.leave_count_balance_increase || 0}</span>
                    </div>` : ''}
                    <div class="bg-amber-50 dark:bg-amber-900/20 rounded p-2 text-center">
                        <span class="block text-xs text-gray-500 dark:text-gray-400">Ngày phép bị trừ</span>
                        <span class="block text-lg font-semibold text-gray-900 dark:text-gray-100">${staff.leave_days || 0}</span>
                    </div>
                    <div class="bg-green-50 dark:bg-green-900/20 rounded p-2 text-center">
                        <span class="block text-xs text-gray-500 dark:text-gray-400">Ngày phép còn lại</span>
                        <span class="block text-lg font-semibold text-gray-900 dark:text-gray-100">${staff.final_leave_day_balance || 0}</span>
                    </div>
                </div>`;

            let overtimeDetailHtml = '';
            if (staff.overtime_hours_normal !== undefined || staff.overtime_hours_sunday !== undefined || staff.overtime_hours_holiday !== undefined) {
                overtimeDetailHtml = `
                <h5 class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mt-4 mb-2">Chi tiết giờ tăng ca</h5>
                <div class="grid grid-cols-3 gap-3">
                    <div class="bg-sky-50 dark:bg-sky-900/20 rounded p-2 text-center">
                        <span class="block text-xs text-gray-500 dark:text-gray-400">TC Thường</span>
                        <span class="block text-lg font-semibold text-gray-900 dark:text-gray-100">${staff.overtime_hours_normal || 0}h</span>
                    </div>
                    <div class="bg-teal-50 dark:bg-teal-900/20 rounded p-2 text-center">
                        <span class="block text-xs text-gray-500 dark:text-gray-400">TC Chủ Nhật</span>
                        <span class="block text-lg font-semibold text-gray-900 dark:text-gray-100">${staff.overtime_hours_sunday || 0}h</span>
                    </div>
                    <div class="bg-fuchsia-50 dark:bg-fuchsia-900/20 rounded p-2 text-center">
                        <span class="block text-xs text-gray-500 dark:text-gray-400">TC Lễ</span>
                        <span class="block text-lg font-semibold text-gray-900 dark:text-gray-100">${staff.overtime_hours_holiday || 0}h</span>
                    </div>
                </div>`;
            } else if (staff.overtime) { // Fallback to old 'overtime' field
                 overtimeDetailHtml = `
                 <div class="grid grid-cols-1 gap-3 mt-3">
                     <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded p-2 text-center">
                         <span class="block text-xs text-gray-500 dark:text-gray-400">Tổng thời gian tăng ca</span>
                         <span class="block text-lg font-semibold text-gray-900 dark:text-gray-100">${staff.overtime}</span>
                     </div>
                 </div>`;
            }

            attendanceSection.innerHTML = `
                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Chi tiết chấm công</h4>
                ${monthInfoHtml}
                ${workDaysDetailHtml}
                ${overtimeDetailHtml}
            `;
            
            // Create card section with salary details
            const salarySection = document.createElement('div');
            salarySection.className = 'p-4';
            
            // Create a more compact salary section
            const salaryDetailsSection = document.createElement('div');
            salaryDetailsSection.className = 'mb-4';
            salaryDetailsSection.innerHTML = `
                <div class="border-b border-gray-200 dark:border-gray-700 pb-4 mb-4">
                    <div class="flex items-center justify-between mb-2">
                        <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">Thông tin lương cơ bản</h4>

                    </div>
                    
                    <div class="grid grid-cols-3 gap-2 text-sm">
                        <div class="flex flex-col">
                            <span class="text-xs text-gray-500 dark:text-gray-400">Lương cơ bản</span>
                            <span class="font-medium text-gray-900 dark:text-gray-100">${formatCurrency(staff.base_salary)}</span>
                        </div>
                        <div class="flex flex-col">
                            <span class="text-xs text-gray-500 dark:text-gray-400">Lương ngày</span>
                            <span class="font-medium text-gray-900 dark:text-gray-100">${formatCurrency(staff.daily_rate)}</span>
                        </div>
                        <div class="flex flex-col">
                            <span class="text-xs text-gray-500 dark:text-gray-400">Phụ cấp</span>
                            <span class="font-medium text-gray-900 dark:text-gray-100">${formatCurrency(staff.base_fixed_allowance)} / ${staff.working_days_in_month} ngày công trong tháng</span>
                        </div>
                    </div>

                    <div class="mt-3 grid grid-cols-3 gap-2 text-sm">
                        <div class="flex items-center">
                            <div class="w-3 h-3 rounded-full bg-green-400 mr-2"></div>
                            <span class="text-xs text-gray-500 dark:text-gray-400">TC thường:</span>
                            <span class="ml-1 font-medium text-gray-900 dark:text-gray-100">${formatCurrency(staff.overtime_hours_normal_rate)}</span>
                        </div>
                        <div class="flex items-center">
                            <div class="w-3 h-3 rounded-full bg-amber-400 mr-2"></div>
                            <span class="text-xs text-gray-500 dark:text-gray-400">TC CN:</span>
                            <span class="ml-1 font-medium text-gray-900 dark:text-gray-100">${formatCurrency(staff.overtime_hours_sunday_rate)}</span>
                        </div>
                        <div class="flex items-center">
                            <div class="w-3 h-3 rounded-full bg-red-400 mr-2"></div>
                            <span class="text-xs text-gray-500 dark:text-gray-400">TC lễ:</span>
                            <span class="ml-1 font-medium text-gray-900 dark:text-gray-100">${formatCurrency(staff.overtime_hours_holiday_rate)}</span>
                        </div>
                    </div>
                </div>
                
                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Kết quả tính lương</h4>
                
                <div class="grid grid-cols-2 gap-3">
                    <!-- Left column: Regular salary -->
                    <div class="space-y-2">
                        <div class="flex justify-between items-center p-2 bg-blue-50 dark:bg-blue-900/10 rounded">
                            <div class="flex items-center">
                                <div class="w-2 h-2 rounded-full bg-blue-500 mr-2"></div>
                                <span class="text-xs text-gray-600 dark:text-gray-400">Lương thường:</span>
                            </div>
                            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">${formatCurrency(staff.normal_days_salary_component)}</span>
                        </div>
                        
                        <div class="flex justify-between items-center p-2 bg-indigo-50 dark:bg-indigo-900/10 rounded">
                            <div class="flex items-center">
                                <div class="w-2 h-2 rounded-full bg-indigo-500 mr-2"></div>
                                <span class="text-xs text-gray-600 dark:text-gray-400">Lương CN:</span>
                            </div>
                            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">${formatCurrency(staff.sunday_days_salary_component)}</span>
                        </div>
                        
                        <div class="flex justify-between items-center p-2 bg-purple-50 dark:bg-purple-900/10 rounded">
                            <div class="flex items-center">
                                <div class="w-2 h-2 rounded-full bg-purple-500 mr-2"></div>
                                <span class="text-xs text-gray-600 dark:text-gray-400">Lương lễ:</span>
                            </div>
                            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">${formatCurrency(staff.holiday_days_salary_component)}</span>
                        </div>
                    </div>
                    
                    <!-- Right column: Overtime -->
                    <div class="space-y-2">
                        <div class="flex justify-between items-center p-2 bg-green-50 dark:bg-green-900/10 rounded">
                            <div class="flex items-center">
                                <div class="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                                <span class="text-xs text-gray-600 dark:text-gray-400">TC thường:</span>
                            </div>
                            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">${formatCurrency(staff.overtime_normal_salary)}</span>
                        </div>
                        
                        <div class="flex justify-between items-center p-2 bg-amber-50 dark:bg-amber-900/10 rounded">
                            <div class="flex items-center">
                                <div class="w-2 h-2 rounded-full bg-amber-500 mr-2"></div>
                                <span class="text-xs text-gray-600 dark:text-gray-400">TC CN:</span>
                            </div>
                            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">${formatCurrency(staff.overtime_sunday_salary)}</span>
                        </div>
                        
                        <div class="flex justify-between items-center p-2 bg-red-50 dark:bg-red-900/10 rounded">
                            <div class="flex items-center">
                                <div class="w-2 h-2 rounded-full bg-red-500 mr-2"></div>
                                <span class="text-xs text-gray-600 dark:text-gray-400">TC lễ:</span>
                            </div>
                            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">${formatCurrency(staff.overtime_holiday_salary)}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Summary section -->
                <div class="mt-4 grid grid-cols-2 gap-3">
                    <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-xs text-gray-500 dark:text-gray-400">Phụ cấp:</span>
                            <span class="text-sm font-medium text-gray-900 dark:text-gray-100">${formatCurrency(staff.fixed_allowance)}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-gray-500 dark:text-gray-400">BHXH:</span>
                            <span class="text-sm font-medium text-red-600 dark:text-red-400">-${formatCurrency(staff.insurance_amount)}</span>
                        </div>
                    </div>
                    
                    <div class="p-2 bg-gradient-to-r from-blue-500 to-indigo-600 rounded text-white flex flex-col justify-center">
                        <div class="text-xs opacity-80">Tổng lương:</div>
                        <div class="text-base font-bold">${formatCurrency(staff.total_salary)}</div>
                    </div>
                </div>
            `;
            
            // Add the details section to the salary section
            salarySection.appendChild(salaryDetailsSection);
            
            // Assemble the card
            card.appendChild(cardHeader);
            card.appendChild(attendanceSection);
            card.appendChild(salarySection);
            
            cardsContainer.appendChild(card);
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
