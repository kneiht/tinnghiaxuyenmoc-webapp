up.compiler('#show-all-jobs', function () {
    const showWeekplan = document.getElementById('show-weekplan');
    const showAllJobs = document.getElementById('show-all-jobs');
    const showGanttJobs = document.getElementById('show-gantt-jobs');
    const showTableJobs = document.getElementById('show-table-jobs');
    const tableChartToggle  = document.getElementById('table-chart-toggle');
    const jobsPlanToggle  = document.getElementById('jobs-plan-toggle');

    showWeekplan.addEventListener('click', function (e) {
        showWeekplan.classList.add('hidden');
        showAllJobs.classList.remove('hidden');
        tableChartToggle.classList.add('hidden');
        ganttChartContainer = document.getElementById('gantt-chart-container');
        ganttChartContainer.classList.add('hidden');
        document.getElementById('display-records').innerHTML = 'loading';
        document.getElementById('create-new').classList.add('disabled');
        document.getElementById('excel-button').classList.add('disabled');
    });

    showAllJobs.addEventListener('click', function (e) {
        showWeekplan.classList.remove('hidden');
        showAllJobs.classList.add('hidden');
        tableChartToggle.classList.remove('hidden');
        document.getElementById('display-records').innerHTML = 'loading';
        document.getElementById('create-new').classList.remove('disabled');
        document.getElementById('excel-button').classList.remove('disabled');
    });


    showGanttJobs.addEventListener('click', function (e) {
        ganttChartContainer = document.getElementById('gantt-chart-container');
        displayRecords = document.getElementById('display-records');
        showGanttJobs.classList.add('hidden');
        showTableJobs.classList.remove('hidden');
        ganttChartContainer.classList.remove('hidden');
        displayRecords.classList.add('hidden');
        fetchAndDrawGanttChart();
    });

    showTableJobs.addEventListener('click', function (e) {
        ganttChartContainer = document.getElementById('gantt-chart-container');
        displayRecords = document.getElementById('display-records');
        showGanttJobs.classList.remove('hidden');
        showTableJobs.classList.add('hidden');
        ganttChartContainer.classList.add('hidden');
        displayRecords.classList.remove('hidden');
    });

});






up.compiler('#check_date', function (element) {
    let checkDate = element;
    // check if there is check_date in params, if yes, set the value of checkDate to it
    let urlParams = new URLSearchParams(window.location.search);
    let check_date = urlParams.get('check_date');
    if (check_date) {
        checkDate.value = check_date;
    }
    else {
        const today = new Date();
        const formattedDate = today.toLocaleDateString('en-CA'); // 'en-CA' gives the ISO-like format (YYYY-MM-DD)
        checkDate.value = formattedDate;
    }

    checkDate.addEventListener('change', function () {
        // let url = window.location.href.split('?')[0] + `?check_date=${checkDate.value}`;

        let showAllJobs = document.getElementById('show-all-jobs');
        if (showAllJobs && showAllJobs.classList.contains('hidden')) {
            let checkDate = document.getElementById('check_date').value;
            let currentUrl = showAllJobs.href
            let url = currentUrl.split('?')[0] + `?check_date=${checkDate}`;
            up.render({ target: '#display-records, #tool-bar, #infor-bar', url: url })
        }

        let showWeekplan = document.getElementById('show-weekplan');
        if (showWeekplan && showWeekplan.classList.contains('hidden')) {
            let checkDate = document.getElementById('check_date').value;
            let currentUrl = showWeekplan.href
            let url = currentUrl.split('?')[0] + `?check_date=${checkDate}`;
            up.render({ target: '#display-records, #tool-bar, #infor-bar', url: url })
        }


    });
});



up.compiler('.select-date', function (selectDate) {
    // If the link is pressed, set the value of check_date to the selected date
    selectDate.addEventListener('click', function () {
        // Get data date
        let dataDate = selectDate.getAttribute('data-date');
        // Set check_date to the selected date
        let checkDate = document.getElementById('check_date');
        checkDate.value = dataDate;

        // Set check_date in url in href if tag <a> with id show-weekplan
        let showWeekplan = document.getElementById('show-weekplan');
        if (showWeekplan) {
            let currentUrl = showWeekplan.href
            let url = currentUrl.split('?')[0] + `?check_date=${dataDate}`;
            showWeekplan.href = url;
        }

        let showAllJobs = document.getElementById('show-all-jobs');
        if (showAllJobs) {
            let currentUrl = showAllJobs.href
            let url = currentUrl.split('?')[0] + `?check_date=${dataDate}`;
            showAllJobs.href = url;
        }
        // up.render({ target: '#display-records', url: url })
    });
})




up.compiler('.just-updated', function (justUpdatedRecord) {
    // Get project id by data from the element project-id
    let projectId = document.getElementById('project-id')
    if (projectId) {
        projectId = projectId.getAttribute('data-id');
    }
    let check_date = document.getElementById('check_date')
    if (check_date) {
        check_date = check_date.value
    };
    if (projectId && check_date) {
        url = `/api/load-element/infor_bar/?page=page_each_project&project_id=${projectId}&check_date=${check_date}`
        console.log(url)
        up.render({ target: '#infor-bar', url: url })
    }
});


// check file size of the upload file, the fuction will be call onchange in the input
function checkFileSize(file) {
    if (file.size > 5 * 1024 * 1024) {
        alert('File phải nhỏ hơn 5 MB');
    }
    return true;
}
// const tasks = [
//     { id: 'Task 1', name: 'Phát rừng tạo mặt bằng', start: new Date(2024, 9, 22), end: new Date(2024, 9, 24), progress: 66 },
//     { id: 'Task 2', name: 'Công việc 2', start: new Date(2024, 11, 22), end: new Date(2024, 12, 22), progress: 22 },
//     { id: 'Task 3', name: 'Công việc 3', start: new Date(2024, 9, 22), end: new Date(2024, 9, 30), progress: 100 },
//     { id: 'Task 4', name: 'Công việc 4', start: new Date(2024, 9, 23), end: new Date(2024, 9, 25), progress: 45 },
//     { id: 'Task 5', name: 'Công việc 5', start: new Date(2024, 9, 23), end: new Date(2024, 9, 27), progress: 80 },
//     { id: 'Task 6', name: 'Công việc 6', start: new Date(2024, 9, 25), end: new Date(2024, 10, 2), progress: 30 },
//     { id: 'Task 7', name: 'Công việc 7', start: new Date(2024, 10, 1), end: new Date(2024, 10, 5), progress: 10 }
// ];

async function fetchAndDrawGanttChart() {
    let ganttChart = document.getElementById('ganttChart');
    let projectID = ganttChart.getAttribute('data-project-id');
    let checkDate = ganttChart.getAttribute('data-check-date');
    let url = `/api/gantt-chart-data/${projectID}/?check_date=${checkDate}`;
    console.log(url);
    const response = await fetch(url);
    const tasks = await response.json();

    // Convert date strings to Date objects
    tasks.forEach(task => {
        const startDate = new Date(task.start);
        startDate.setHours(0, 0, 0, 0);
        task.start = startDate;

        const endDate = new Date(task.end);
        endDate.setHours(0, 0, 0, 0);
        task.end = endDate;
    });
    drawGanttChart(tasks);
}

function drawGanttChart(tasks) {
    // Remove previous gantt chart
    const ganttChart = document.getElementById('ganttChart');
    ganttChart.innerHTML = '';
    const margin = { top: 40, right: 40, bottom: 40, left: 150 };
    const width = document.getElementById('ganttChart').offsetWidth - margin.left - margin.right;
    const height = tasks.length * 50 + margin.top + margin.bottom;
    
    const svg = d3.select("#ganttChart")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left}, ${margin.top})`);

    const x = d3.scaleTime()
        .domain([d3.min(tasks, d => d.start), d3.max(tasks, d => d.end)])
        .range([0, width]);

    const y = d3.scaleBand()
        .domain(tasks.map(d => d.name))
        .range([0, height - margin.top - margin.bottom])
        .padding(0.1);

    // Grid lines
    svg.append("g")
        .attr("class", "grid")
        .call(d3.axisBottom(x).ticks(5).tickSize(-height + margin.top + margin.bottom).tickFormat(''))
        .attr("transform", `translate(0, ${height - margin.top - margin.bottom})`)
        .attr("class", "text-gray-700 dark:text-gray-300");

    // Axis x => show date
    svg.append("g")
        .call(d3.axisBottom(x).tickFormat(d3.timeFormat("%d-%m-%Y")))
        .attr("transform", `translate(0, ${height - margin.top - margin.bottom})`)
        .attr("class", "text-gray-700 dark:text-gray-300");



    // // X-axis with task-specific start and end dates
    // svg.append("g")
    //     .call(d3.axisBottom(x)
    //         .tickValues(tasks.flatMap(d => [d.start, d.end]))  // Custom tick values for each task's start and end date
    //         .tickFormat(d3.timeFormat("%d-%m-%Y"))  // Date format for ticks
    //     )
    //     .attr("transform", `translate(0, ${height - margin.top - margin.bottom})`)
    //     .attr("class", "text-gray-700 dark:text-gray-300");



    svg.append("g")
        .call(d3.axisLeft(y))
        .attr("class", "text-gray-700 dark:text-gray-300");


    const color = d3.scaleLinear()
        .domain([0, 50, 100])
        .range(["#ff8a65", "#ffd54f", "#4caf50"]); // Different colors for progress

    svg.selectAll("rect")
        .data(tasks)
        .enter()
        .append("rect")
        .attr("x", d => x(d.start))
        .attr("y", d => y(d.name))
        .attr("y", d => y(d.name))
        .attr("width", d => x(d.end) - x(d.start))
        .attr("height", y.bandwidth())
        .attr("fill", d => color(d.progress))  // Dynamic color based on progress
        .attr("rx", 6)  // More rounded corners
        .attr("class", "shadow-lg transition-all duration-300");

    svg.selectAll("text.progress")
        .data(tasks)
        .enter()
        .append("text")
        .attr("x", d => x(d.start) + 5)
        .attr("y", d => y(d.name) + y.bandwidth() / 2 + 4)
        .text(d => `${d.progress}%`)
        .attr("class", "text-gray-800 dark:text-gray-300 font-semibold");

    // Tooltip for interactivity
    const tooltip = d3.select("body")
        .append("div")
        .attr("class", "hidden absolute bg-white dark:bg-gray-800 p-3 rounded-lg shadow-md text-gray-800 dark:text-gray-300");

    svg.selectAll("rect")
        .on("mouseover", function (event, d) {
            tooltip.classed("hidden", false)
                .html(`<strong>${d.name}</strong><br>Start: ${d3.timeFormat("%d-%m-%Y")(d.start)}<br>End: ${d3.timeFormat("%d-%m-%Y")(d.end)}<br>Progress: ${d.progress}%`)
                .style("left", `${event.pageX + 5}px`)
                .style("top", `${event.pageY - 28}px`);
        })
        .on("mouseout", function () {
            tooltip.classed("hidden", true);
        });


    // Find all <text> elements that match the specified attributes
    textElements = ganttChart.querySelectorAll('text[fill="currentColor"][x="-9"][dy="0.32em"]');
    
    // Log the found elements to the console
    textElements.forEach((element, index) => {
        // Calcuate the width of the element
        let width = element.getBBox().width;

        // Get the original text
        const textContent = element.textContent;
        console.log(`Original text: ${textContent}`);

        // Create a helper function to measure text width dynamically
        function measureTextWidth(text, element) {
            element.textContent = text
            textWidth = element.getBBox().width;
            return  textWidth
        }

        // Split the text into multiple lines, each with a max width of 100px
        const maxWidth = 120; // Maximum width in pixels
        let words = textContent.split(' '); // Split text into words
        let currentLine = '';
        let lines = [];

        words.forEach((word) => {
            let testLine = currentLine ? currentLine + ' ' + word : word;
            let testWidth = measureTextWidth(testLine, element);
            if (testWidth <= maxWidth) {
                currentLine = testLine; // Add the word to the current line
            } else {
                lines.push(currentLine); // Push the current line and start a new one
                currentLine = word;
            }
        });

        if (currentLine) {
            lines.push(currentLine); // Push the last line
        }
        console.log(lines)

        // Make copies of element for each line, change x to make the lines separate
        // then remove the old element and add the new ones
        element.textContent = ''
        const offset = (lines.length-1) * 6
        lines.forEach((line, index) => {
            
            const newElement = element.cloneNode(true);
            newElement.textContent = line;
            newElement.setAttribute('y', `${index * 12 - offset}`);
            element.parentNode.appendChild(newElement);
            
        });

        // // Remove the old text element
        // element.remove();
    });

    
}


