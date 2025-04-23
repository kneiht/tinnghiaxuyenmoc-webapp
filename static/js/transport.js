
up.compiler('.transport-table', function (transportTable) {
    var editButton = transportTable.querySelector('#edit');
    var saveButton = transportTable.querySelector('#save');
    var cancelButton = transportTable.querySelector('#cancel');
    var addButton = transportTable.querySelector('#add');




    // Listen to the edit button, if it is clicked, hide the edit button and show the save button
    editButton.addEventListener('click', function (event) {
        // prevent form from submitting
        event.preventDefault();
        editButton.classList.add('hidden');
        saveButton.classList.remove('hidden');
        addButton.classList.remove('hidden');
        cancelButton.classList.remove('hidden');
        showInput();
    })

    // Listen to the save button, if it is clicked, hide the save button and show the edit button
    // saveButton.addEventListener('click', function (event) {
    //     editButton.classList.remove('hidden');
    //     saveButton.classList.add('hidden');
    //     addButton.classList.add('hidden');
    //     cancelButton.classList.add('hidden');
    //     showDisplay();
    // })

    // Listen to the cancel button, if it is clicked, hide the save button and show the edit button
    cancelButton.addEventListener('click', function (event) {
        // prevent form from submitting
        event.preventDefault();
        editButton.classList.remove('hidden');
        saveButton.classList.add('hidden');
        addButton.classList.add('hidden');
        cancelButton.classList.add('hidden');
        // remove all add-row-template
        var addRowTemplates = transportTable.querySelectorAll('.add-row-template');
        addRowTemplates.forEach(function (addRowTemplate) {
            if (addRowTemplate.classList.contains('hidden')) {
                return;
            }
            addRowTemplate.remove();
        })
        showDisplay();
    })

    addButton.addEventListener('click', function (event) {
        // prevent form from submitting
        event.preventDefault();
        // Get rowplate by coying the row name add-row-template
        var addRowTemplate = transportTable.querySelector('.add-row-template');
        var index = transportTable.querySelectorAll('.add-row-template').length;

        // Clone the rowplate and append it to the table    
        var newRow = addRowTemplate.cloneNode(true);
        // Replace the rowplate with the new row
        transportTable.querySelector('table').appendChild(newRow);

        // count the number of add-row-template
        var addRowTemplates = transportTable.querySelectorAll('.add-row-template');
        

        // find all input and select elements in the new row and remove disabled
        newRow.querySelectorAll('input, select, textarea').forEach(function (element) {
            element.removeAttribute('disabled');
            // Add index to the name attribute of the input element
            element.name = element.name + '_' + index;
        })
        // unhide
        newRow.classList.remove('hidden');
    })


    // Write function find and hide or show element with class display and input
    function showDisplay() {
        var inputs = transportTable.querySelectorAll('.input');
        var displays = transportTable.querySelectorAll('.display');
        // Show all display elements
        inputs.forEach(function (input) {
            input.classList.add('hidden');
        });

        // Hide all display elements
        displays.forEach(function (display) {
            display.classList.remove('hidden');
        });
    }

    function showInput() {
        var inputs = transportTable.querySelectorAll('.input');
        var displays = transportTable.querySelectorAll('.display');
        // Show all input elements
        displays.forEach(function (display) {
            display.classList.add('hidden');
        });

        // Hide all input elements
        inputs.forEach(function (input) {
            input.classList.remove('hidden');
        });
    }   


});


up.compiler('#start_date', function (element) {
    let startDate = element;
    startDate.addEventListener('change', function () {
        // Get the selected start date value
        let newStartDate = startDate.value;

        // Find all <a> tags in database-selection
        let databaseSelection = document.getElementById('nav_menu');
        if (!databaseSelection) {
            return;
        }
        let aTags = databaseSelection.querySelectorAll('a');

        // For each <a> tag
        aTags.forEach(function (aTag) {
            let currentUrl = new URL(aTag.href); // Convert href to URL object

            // Check if 'start_date' exists in the query parameters
            if (currentUrl.searchParams.has('start_date')) {
                // If it exists, replace with new start_date
                currentUrl.searchParams.set('start_date', newStartDate);
            } else {
                // If it doesn't exist, append the new start_date
                currentUrl.searchParams.append('start_date', newStartDate);
            }

            // Update the href with the modified URL
            aTag.href = currentUrl.toString();
        });
    });
});



up.compiler('#end_date', function (element) {
    let endDate = element;
    endDate.addEventListener('change', function () {
        // Get the selected start date value
        let newendDate = endDate.value;

        // Find all <a> tags in database-selection
        let databaseSelection = document.getElementById('nav_menu');
        if (!databaseSelection) {
            return;
        }
        let aTags = databaseSelection.querySelectorAll('#driver_salary, #vehicle_revenue');
        
        if (!aTags) {
            return;
        }
        // For each <a> tag
        aTags.forEach(function (aTag) {
            let currentUrl = new URL(aTag.href); // Convert href to URL object

            // Check if 'start_date' exists in the query parameters
            if (currentUrl.searchParams.has('end_date')) {
                // If it exists, replace with new start_date
                currentUrl.searchParams.set('end_date', newendDate);
            } else {
                // If it doesn't exist, append the new start_date
                currentUrl.searchParams.append('end_date', newendDate);
            }

            // Update the href with the modified URL
            aTag.href = currentUrl.toString();
        });


    });
});



up.compiler('.transport-table', function (table) {
    // Get all the input which has class iput-driver
    let inputs = table.querySelectorAll('.input-driver');
    // Listen to it, if the value is changed, update all other inputs
    inputs.forEach(function (input) {
        input.addEventListener('change', function () {
            inputs.forEach(function (otherInput) {
                if (otherInput !== input && !otherInput.value) {
                    otherInput.value = input.value;
                    // Also find ".select-wrapper" below the input element and update the text
                    let selectWrapper = otherInput.parentNode.querySelector('.select-wrapper');
                    if (selectWrapper) {
                        selectWrapper.querySelector('.selected-option').textContent = input.options[input.selectedIndex].text;
                    }   
                }
            });
        });
    });
});








function calculatePLTotals() {
    const table = document.getElementById('display-table-records');
    if (!table) return false;

    // Define column indices and their corresponding total element IDs
    const columnMappings = {
        4: 'total-hours',
        5: 'total-revenue',
        6: 'total-fuel',
        7: 'total-oil',
        8: 'total-repair',
        9: 'total-depreciation',
        10: 'total-interest',
        11: 'total-base-salary',
        12: 'total-hourly-salary',
        13: 'total-cost',
        14: 'total-profit'
    };

    // Get all rows in <tbody>
    const rows = table.querySelectorAll('tbody tr');

    // Initialize totals for each column
    const totals = {};
    Object.keys(columnMappings).forEach(index => {
        totals[index] = 0;
    });

    // Function to extract numeric value from a cell
    // const extractNumber = (text) => {
    //     if (!text) return 0;
    //     return parseFloat(text.replace(/[^0-9.-]+/g, '')) || 0;
    // };

    // Function to extract numeric value from a cell
    const extractNumber = (text) => {
        if (!text) return 0;
        
        // Find all numbers in the text (including negative numbers)
        const numbers = text.match(/-?[\d,]+(\.\d+)?/g) || [];
        
        // Sum all found numbers
        return numbers.reduce((sum, numStr) => {
            // Convert each number string to a float
            const value = parseFloat(numStr.replace(/[^0-9.-]+/g, '')) || 0;
            return sum + value;
        }, 0);
    };


    // Calculate totals for each column
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 15) {
            Object.keys(columnMappings).forEach(index => {
                const cell = cells[index];
                if (cell) {
                    totals[index] += extractNumber(cell.textContent);
                }
            });
        }
    });

    // Update the footer cells with formatted totals
    Object.keys(columnMappings).forEach(index => {
        const elementId = columnMappings[index];
        const element = document.getElementById(elementId);
        if (element) {
            // Format with 2 decimal places for hours, 0 for others
            const value = index == 4 ? totals[index].toFixed(2) : totals[index].toFixed(0);
            console.log("nothing")
            element.textContent = formatNumber(value);
        }
    });

    // For backward compatibility, also update the old display elements if they exist
    const totalRevenueElement = document.getElementById('total-revenue-display');
    const totalInterestElement = document.getElementById('total-interest-display');

    if (totalRevenueElement) {
        totalRevenueElement.innerHTML = `Tổng doanh thu: ${formatNumber(totals[5])} VNĐ`;
    }

    if (totalInterestElement) {
        if (totals[14] < 0) {
            totalInterestElement.classList.add('text-red-700');
            totalInterestElement.classList.add('bg-red-100');
        } else {
            totalInterestElement.classList.remove('text-red-700');
            totalInterestElement.classList.remove('bg-red-100');
        }
        totalInterestElement.innerHTML = `Tổng lợi nhuận: ${formatNumber(totals[14])} VNĐ`;
    }

    return true;
}


function calculatePLTotalsToolbar() {
    const table = document.getElementById('display-table-records');
    if (!table) return false;
    const headerRow = table.querySelector('thead tr');
    const revenueColumn = Array.from(headerRow.children).find(th => th.textContent.trim() === "Doanh thu");
    const revenueIndex = revenueColumn ? Array.from(headerRow.children).indexOf(revenueColumn) : -1;
    const interestColumn = Array.from(headerRow.children).find(th => th.textContent.trim() === "Lợi nhuận");
    const interestIndex = 14;

    if (revenueIndex == -1 && interestIndex == -1) {
        return false;
    }

    // Get all rows in <tbody>
    const rows = table.querySelectorAll('tbody tr');
    // Calculate sum of the values in that column
    let totalRevenue = 0;
    let totalInterest = 0;


    const calculateTotal = (index) => {
        return (total, row) => {
            const cell = row.children[index];
            if (cell) {
                const value = parseFloat(cell.textContent.replace(/[^0-9.-]+/g, '')); // Remove non-numeric characters
                if (!isNaN(value)) {
                    return total + value;
                }
            }
            return total;
        }
    };

    const calcRevenue = calculateTotal(revenueIndex);
    const calcInterest = calculateTotal(interestIndex);

    rows.forEach(row => {
        totalRevenue = calcRevenue(totalRevenue, row);
        totalInterest = calcInterest(totalInterest, row);
    });


    // Display the sum in this innerText
    const totalRevenueElement = document.getElementById('total-revenue-toolbar')
    const totalCostElement = document.getElementById('total-cost-toolbar')
    const totalInterestElement = document.getElementById('total-interest-toolbar')

    if (totalInterest < 0) {
        totalInterestElement.classList.add('text-red-700');
        totalInterestElement.classList.add('bg-red-100');
    }
    totalRevenueElement.innerHTML = `Tổng doanh thu: ${formatNumber(totalRevenue.toFixed(0))} VNĐ`;
    totalInterestElement.innerHTML = `Tổng lợi nhuận: ${formatNumber(totalInterest.toFixed(0))} VNĐ`;

};


up.compiler('#display-table-records', function (table) {
    const currentUrl = window.location.href;
    if (currentUrl.includes('ConstructionReportPL')) {
        // Function to check for "Đang tải dữ liệu" in the table
        const checkLoadingData = async () => {
            const rows = table.querySelectorAll('tbody tr');
            let isLoadingData = false;
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                cells.forEach(cell => {
                    if (cell.textContent.includes("Đang tải dữ liệu")) {
                        isLoadingData = true;
                    }
                });
            });

            // If "Đang tải dữ liệu" is not found, calculate totals
            if (!isLoadingData) {
                calculatePLTotals();
                calculatePLTotalsToolbar();
            } else {
                // If still loading, check again after 1000ms
                setTimeout(checkLoadingData, 1000);
            }
        };

        // Start checking for loading data
        checkLoadingData();
    }
});

