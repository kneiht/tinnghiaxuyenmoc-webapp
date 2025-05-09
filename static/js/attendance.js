up.compiler('.display-calendar', function (modalForm) {
    const monthYear = document.getElementById('monthYear');
    const calendarDays = document.getElementById('calendarDays');
    const prevMonthBtn = document.getElementById('prevMonth');
    const nextMonthBtn = document.getElementById('nextMonth');
    const staffSelect = document.getElementById('staffSelect');
    const monthSelect = document.getElementById('monthSelect');

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
            return data.records || [];
        } catch (error) {
            console.error('Error fetching attendance data:', error);
            return [];
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

        // Fetch attendance data for the current month and staff
        attendanceData = await fetchAttendanceData();
        console.log('Fetched attendance data:', attendanceData);

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
            dayCell.classList.add('py-2', 'rounded', 'cursor-pointer', 'border', 'border-gray-300', 'dark:border-gray-600', 'min-h-[100px]', 'flex', 'flex-col');

            // Add day number
            const dayNumber = document.createElement('div');
            dayNumber.textContent = day;
            dayNumber.classList.add('font-semibold', 'mb-1');
            dayCell.appendChild(dayNumber);

            // Highlight today
            const today = new Date();
            if (day === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
                dayCell.classList.add('bg-blue-100', 'dark:bg-blue-500');
            } else {
                dayCell.classList.add('hover:bg-blue-100', 'dark:hover:bg-blue-500');
            }

            // Add double-click event to open attendance form
            if (staffSelect.value && staffSelect.value !== 'all') {
                dayCell.addEventListener('dblclick', () => {
                    const dateStr = `${year}-${(month + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
                    const existingRecord = findAttendanceRecord(day, year, month);
                    openAttendanceModal(dateStr, existingRecord);
                });
            }

            // Add attendance data if available
            const record = findAttendanceRecord(day, year, month);
            if (record) {
                // Apply background color based on attendance status
                let bgColorClass = '';
                switch (record.attendance_status) {
                    case 'present':
                        bgColorClass = ['bg-green-100', 'dark:bg-green-900'];
                        break;
                    case 'excused_absence':
                        bgColorClass = ['bg-yellow-100', 'dark:bg-yellow-900'];
                        break;
                    case 'unexcused_absence':
                        bgColorClass = ['bg-red-100', 'dark:bg-red-900'];
                        break;
                }

                // Apply background color to the cell
                dayCell.classList.add(bgColorClass);

                // Create attendance info container
                const attendanceInfo = document.createElement('div');
                attendanceInfo.classList.add('text-xs', 'mt-1');

                // Add status badge
                const statusBadge = document.createElement('div');
                let badgeClass = 'inline-block px-2 py-1 rounded-full text-xs font-semibold mb-1 ';

                switch (record.attendance_status) {
                    case 'present':
                        badgeClass += 'bg-green-500 text-white';
                        break;
                    case 'excused_absence':
                        badgeClass += 'bg-yellow-500 text-white';
                        break;
                    case 'unexcused_absence':
                        badgeClass += 'bg-red-500 text-white';
                        break;
                }

                statusBadge.className = badgeClass;

                // Map status to Vietnamese
                let statusText = '';
                switch (record.attendance_status) {
                    case 'present':
                        statusText = 'Có mặt';
                        break;
                    case 'excused_absence':
                        statusText = 'Vắng có phép';
                        break;
                    case 'unexcused_absence':
                        statusText = 'Vắng không phép';
                        break;
                }
                statusBadge.textContent = statusText;
                attendanceInfo.appendChild(statusBadge);

                // Add work day count with badge
                const workDayBadge = document.createElement('div');
                workDayBadge.className = 'inline-block px-2 py-1 bg-blue-500 text-white rounded-full text-xs font-semibold ml-1';
                workDayBadge.textContent = `${record.work_day_count}`;
                attendanceInfo.appendChild(workDayBadge);

                // Add a line break
                attendanceInfo.appendChild(document.createElement('br'));

                // Add note if available
                if (record.note) {
                    const noteDiv = document.createElement('div');
                    noteDiv.textContent = record.note;
                    noteDiv.className = 'text-gray-600 dark:text-gray-400 italic mt-1 text-xs overflow-hidden';
                    noteDiv.style.display = '-webkit-box';
                    noteDiv.style.webkitLineClamp = '2';
                    noteDiv.style.webkitBoxOrient = 'vertical';
                    attendanceInfo.appendChild(noteDiv);
                }

                dayCell.appendChild(attendanceInfo);
            }

            calendarDays.appendChild(dayCell);
        }
    }

    prevMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar(currentDate);
    });

    nextMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar(currentDate);
    });

    // Listen for staff selection changes
    staffSelect.addEventListener('change', () => {
        renderCalendar(currentDate);
    });

    // Listen for month select input changes
    monthSelect.addEventListener('change', () => {
        if (monthSelect.value) {
            const [year, month] = monthSelect.value.split('-').map(Number);
            currentDate = new Date(year, month - 1, 1);
            renderCalendar(currentDate);
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
        });
    }

    // Attendance Modal Functions
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
    const workDayCountSelect = document.getElementById('workDayCount');
    const attendanceStatusSelect = document.getElementById('attendanceStatus');
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

        // If editing existing record
        if (record) {
            recordIdInput.value = record.id;
            workDayCountSelect.value = parseFloat(record.work_day_count).toFixed(1);
            attendanceStatusSelect.value = record.attendance_status;
            noteInput.value = record.note || '';
            deleteRecordBtn.classList.remove('hidden');
            console.log(record);

        } else {
            recordIdInput.value = '';
            workDayCountSelect.value = '1.0';
            attendanceStatusSelect.value = 'present';
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

    // Handle form submission
    attendanceForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = {
            record_id: recordIdInput.value || null,
            staff_id: staffIdInput.value,
            date: recordDateInput.value,
            work_day_count: workDayCountSelect.value,
            attendance_status: attendanceStatusSelect.value,
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
                    workDayCountSelect.value = parseFloat(data.record.work_day_count).toFixed(1);
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
});