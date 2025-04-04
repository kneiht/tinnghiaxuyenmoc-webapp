up.compiler('#modal_form', function (modalForm) {
    modalForm.addEventListener('submit', function (submitEvent) {
        // Find all file input elements inside the modal
        const fileInputs = modalForm.querySelectorAll('input[type="file"]');

        fileInputs.forEach(fileInput => {
            const file = fileInput.files[0];
            const maxSize = 5 * 1024 * 1024; // 5MB

            if (file && file.size > maxSize) {
                fileErrorText = document.getElementById('fileError');
                fileErrorText.textContent = "File quá lớn! Vui lòng chọn file nhỏ hơn 5MB.";
                fileErrorText.classList.remove("hidden")

                submitEvent.preventDefault(); // Prevent form submission
                enableSubmitButton();
            } else {
                fileErrorText = document.getElementById('fileError');
                fileErrorText.classList.add("hidden");
            }
        });
    });
});


up.compiler('.change-page', function (changePage) {
    changePage.addEventListener('click', function () {
        // Get the display name and replace the title
        const displayName = changePage.textContent.trim();
        document.title = displayName;
    });
});

function updateUrlParams(currentUrl, paramsToUpdate) {
    // console.log("Current URL:", currentUrl);
    // Convert the current URL to a URL object if the url is not already a URL object
    if (!(currentUrl instanceof URL)) {
        currentUrl = new URL(currentUrl);
    }

    // Get the search parameters from the URL
    const searchParams = new URLSearchParams(currentUrl.search);
    // Update the parameters with the new values
    for (const [key, value] of Object.entries(paramsToUpdate)) {
        searchParams.set(key, value);
    }
    // Create the new URL with the updated parameters
    const newUrl = `${currentUrl.origin}${currentUrl.pathname}?${searchParams.toString()}`;
    // Log the new URL to the console
    // console.log("New URL:", newUrl);
    // Return the new URL
    return newUrl;
}



function changeUrl(newUrl) {
    // Create a new state object (it can be anything, or even null)
    var stateObj = { foo: "bar" };
    // Use history.pushState to change the URL
    history.pushState(stateObj, "page title", newUrl);
}

// CSRF TOKEN =========================================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');




// NAVIGATION BAR ITEMS =========================================
up.compiler('#nav_bar', function (element) {

    function activeMenuItem(item) {
        // Remove specific classes from all <a> elements within #nav_bar_left
        document.querySelectorAll('#nav_bar_left a').forEach(link => {
            link.classList.remove('border');
            link.classList.remove('bg-gray-200');
            link.classList.remove('border-gray-300');
            link.classList.remove('dark:bg-gray-800');
            link.classList.remove('dark:border-gray-700');
        });

        // Add classes to the clicked element (referred to as 'item')
        item.classList.add('bg-gray-200');
        item.classList.add('border');
        item.classList.add('border-gray-300');
        item.classList.add('dark:bg-gray-800');
        item.classList.add('dark:border-gray-700');
    }

    // Add event listener to each navigation item
    document.querySelectorAll('#nav_bar_left a').forEach(item => {
        item.addEventListener('click', function () {
            activeMenuItem(item);
        });

        // Check if the item url equals to the current url => active the item
        const itemUrl = item.getAttribute('href');
        const currentUrl = window.location.pathname;
        const currentUrlParts = currentUrl.split('/');
        const itemUrlParts = itemUrl.split('/');
        if (itemUrlParts[1] === currentUrlParts[1]) {
            activeMenuItem(item);
        }
    });
});



// THEME CHANGE =========================================
up.compiler('#theme-toggle', function (element) {
    const themeToggles = document.querySelectorAll('#theme-toggle');
    const storedTheme = localStorage.getItem('theme');
    // console.log(storedTheme);
    function updateTheme(isDark) {
        const sunIcon = document.getElementById('sun-icon');
        const moonIcon = document.getElementById('moon-icon');
        // Update theme class
        document.documentElement.classList.toggle('dark', isDark);

        // Update data-theme attribute of the tag html
        document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');


        localStorage.setItem('theme', isDark ? 'dark' : 'light');

        // Update icons for all sun and moon instances
        sunIcon.style.opacity = isDark ? '0' : '1';
        moonIcon.style.opacity = isDark ? '1' : '0';
    }

    // Event listener for each theme toggle
    themeToggles.forEach(toggle => {
        toggle.addEventListener('change', () => {
            updateTheme(toggle.checked);
        });
    });

    // Check for stored theme preference and apply it
    if (storedTheme) {
        const isDark = storedTheme === 'dark';
        updateTheme(isDark);
        themeToggles.forEach(toggle => {
            toggle.checked = isDark;
        });
    }
});



// DROPDOWN MENUS =========================================
up.compiler('.menu', function (element) {
    // Function to show a menu
    function showHideMenu(menu, action) {
        var dropdownMenu = menu.querySelector('.dropdown-menu');
        if (dropdownMenu) {
            if (action === 'show') {
                dropdownMenu.classList.remove('hidden');
            }
            else if (action === 'hide') {
                dropdownMenu.classList.add('hidden');
            }
            else if (action === 'toggle') {
                dropdownMenu.classList.toggle('hidden');
            }
        }
    }
    // Attach click event listeners to menu buttons
    element.querySelector('.menu-button').addEventListener('click', function () {
        showHideMenu(element, 'toggle')
        // Hide all other menus when click to a menu
        document.querySelectorAll('.menu').forEach(menu => {
            if (menu !== element) {
                showHideMenu(menu, 'hide')
            }
        })
    });

    // Hide menus when clicking outside of them
    document.addEventListener('click', function (event) {
        if (!element.contains(event.target)) {
            showHideMenu(element, 'hide')
        }
    })



});





// RESPONSIVE ELEMENTS ON RESIZE =========================================
up.compiler('.display-cards', function (element) {
    // count the number of cards in display-cards then put in the element with id "count"
    const displayCards = element;
    const count = displayCards.children.length;
    if (document.getElementById("count")) {
        document.getElementById("count").textContent = "Count: " + count;
    }
    // Function to adjust the number of grid columns
    function adjustGridColumns() {
        const container = element;
        if (!container) return;

        const containerWidth = container.offsetWidth;
        if (containerWidth === 0) {
            return;
        }
        // Remove all previous grid classes
        container.className = container.className.replace(/grid-cols-\d+/g, '');

        // Calculate the number of columns, ensuring at least 1 column
        var gridNum = Math.max(1, Math.round((containerWidth - 10) / 360));

        // Optionally, set a maximum number of columns
        const maxColumns = 10; // For example, a maximum of 5 columns
        gridNum = Math.min(gridNum, maxColumns);

        container.classList.add('grid-cols-' + gridNum); // Adjust number of columns as needed
        // Display the display-cards container after the grid has been adjusted for the first time  
        container.classList.remove("opacity-0")
        container.classList.add("opacity-100")

        // Get all the .display-cards then apply the grid class of the display-cards which has the highest number of columns to the others
        const displayCards = document.querySelectorAll('.display-cards');
        // Apply the highest number of columns to the others
        displayCards.forEach(displayCard => {
            displayCard.className = displayCard.className.replace(/grid-cols-\d+/g, '');
            displayCard.classList.add('grid-cols-' + gridNum);
            displayCard.classList.remove("opacity-0")
            displayCard.classList.add("opacity-100")
        });
    }
    // Call this in your sidebar toggle function
    // toggleSidebarFunction() { ... adjustGridColumns(); ... }

    // Initial adjustment
    adjustGridColumns();
    window.addEventListener('resize', adjustGridColumns);

});





up.compiler('#record-edit', function (recordEdit) {
    function getClosestRecordElement() {
        let closestRecord = recordEdit.closest('[id*="record_"]');
        closestRecord.addEventListener('dblclick', function () {
            recordEdit.click();
        });

    }
    getClosestRecordElement();
});


up.compiler('.expand', function (expand) {
    // Add event listener to the document
    document.addEventListener('click', function (event) {
        // If the target is not the expand element, then remove the style height
        if (event.target !== expand) {
            expand.style.height = '';
        }
    });
    // Add event listener to the document
    document.addEventListener('focus', function (event) {
        // If the target is not the expand element, then remove the style height
        if (event.target !== expand) {
            expand.style.height = '';
        }
    });
    // Add event listener to the expand element
    expand.addEventListener('click', function () {
        // Add style height 100px
        expand.style.height = '150px';
    });
    expand.addEventListener('focus', function () {
        // Add style height 100px
        expand.style.height = '150px';
    });
});



// up.compiler('.form-input', function(inputfield) {
//     // Check if the input field is a number field by getting the input type
//     if (inputfield.type !== 'number') {
//         // Set the input type to 'text' for flexible formatting
//         inputfield.type = 'text';
//     }

//     // Function to format the number with commas
//     function formatNumber(value) {
//         var n = parseInt(value.replace(/\D/g, ''), 10);
//         return isNaN(n) ? '' : n.toLocaleString();
//     }

//     // Initialize the field value if present
//     inputfield.value = formatNumber(inputfield.value);

//     // Add keyup event listener to format the value and update tooltip
//     inputfield.addEventListener('keyup', function() {
//         // Format the value with commas and set it back to the input
//         this.value = formatNumber(this.value);

//         // Update the tooltip (title attribute) with the formatted number
//         this.title = this.value;
//     });
// });


function formatNumber(number) {
    // Check if the number is a valid number
    if (number === '' || isNaN(parseFloat(number))) {
        return '';
    }

    // Convert the number to a float, just in case it's passed as a string
    let num = parseFloat(number);

    // Convert the number to a string with two decimal places
    let parts = num.toString().split('.');

    // Add thousand separators (dots) to the integer part
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');

    // Join the integer and fractional parts with a comma
    return parts.join('.');
}
up.compiler('.form-input', function (inputfield) {
    if (inputfield.classList.contains('no-readable')) {
        return;
    }

    // Check if the input field is a number field by getting the input type
    if (inputfield.type !== 'number') {
        return;
    }

    function formatNumber(number) {
        // Check if the number is a valid number
        if (number === '' || isNaN(parseFloat(number))) {
            return '';
        }

        // Convert the number to a float, just in case it's passed as a string
        let num = parseFloat(number);

        // Convert the number to a string with two decimal places
        let parts = num.toString().split('.');

        // Add thousand separators (dots) to the integer part
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');

        // Join the integer and fractional parts with a comma
        return parts.join(',');
    }

    function formatVerboseCurrency(number) {
        if (isNaN(number) || number < 0) {
            return "Invalid input";
        }

        const billion = 1000000000;
        const million = 1000000;
        const thousand = 1000;

        let result = "";

        // Handle billions
        if (number >= billion) {
            const billions = Math.floor(number / billion);
            result += `${billions} tỷ `;
            number %= billion;
        }

        // Handle millions
        if (number >= million) {
            const millions = Math.floor(number / million);
            result += `${millions} triệu `;
            number %= million;
        }

        // Handle thousands
        if (number >= thousand) {
            const thousands = Math.floor(number / thousand);
            result += `${thousands} ngàn `;
            number %= thousand;
        }

        // Handle the remaining units
        if (number > 0) {
            result += `${number} `;
        }

        // Append "đồng" at the end
        result += "đồng";

        // Remove any extra spaces and return the result
        return result.replace(/\s+/g, ' ').trim();
    }



    // Create a popup element
    const popup = document.createElement('div');
    popup.classList.add('text-blue-500');
    popup.classList.add('ms-3');

    function formatPopup(popup, inputfield) {
        const listVerbose = ['requested_amount', 'transferred_amount'];
        // If name attribute = requested_amount, use formatVerBoseCurrency
        if (listVerbose.includes(inputfield.name)) {
            popup.innerText = formatVerboseCurrency(inputfield.value);
        }
        else {
            popup.innerText = formatNumber(inputfield.value);
        }
    }


    // Insert the popup after the input field
    formatPopup(popup, inputfield)
    inputfield.parentNode.insertBefore(popup, inputfield.nextSibling);

    // Add keyup event listener to format the value and update tooltip
    inputfield.addEventListener('keyup', function () {
        formatPopup(popup, inputfield)
    });

});

function handleNewSelectElement(select) {
    // If there are only about 5 options, don't create the wrapper
    if ((select.options.length <= 6 && !select.hasAttribute('readonly')) && !select.classList.contains('new-select')) {
        return;
    }

    // id =sort-select
    if (select.id === 'sort-select') {
        return;
    }

    // Check if there an element ".select-wrapper" below the select element => return
    if (select.parentNode.querySelector('.select-wrapper')) {
        // delete the element ".select-wrapper" below the select element
        select.parentNode.querySelector('.select-wrapper').remove();
    }
    // Create the wrapper div for card and dropdown
    const wrapper = document.createElement('div');
    const width = select.style.width;
    if (width) {
        wrapper.style.width = width;
    }
    wrapper.classList.add('select-wrapper', 'relative'); // Add TailwindCSS classes for positioning and spacing


    // Create the card element
    const card = document.createElement('div');
    Array.from(select.classList).forEach(c => {
        card.classList.add(c);
    });
    card.classList.add('form-input', 'cursor-pointer');
    card.innerHTML = `
      <div class="card-body flex items-center justify-between">
        <span class="selected-option text-nowrap overflow-hidden">${select.options[select.selectedIndex]?.text || 'Select an option'}</span>
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-500 dark:text-gray-400" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </div>
    `;

    if (select.hasAttribute('readonly')) {
        // Hide the arror icon
        card.querySelector('svg').style.display = 'none';
    }

    // Create the dropdown element
    const dropdown = document.createElement('div');
    dropdown.classList.add(
        'dropdown',
        'hidden',
        'absolute',
        'left-0',
        'right-0',
        'bg-white',
        'dark:bg-gray-900',
        'border',
        'dark:border-gray-700',
        'rounded-md',
        'shadow-lg',
        'mt-1',
        'z-10',
    );

    // Create the input for filtering
    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = 'Tìm ...';
    input.classList.add(
        'text-sm',
        'w-full',
        'p-2',
        'border-b',
        'border-slate-300',
        'dark:border-slate-600',
        'outline-none',
        'dark:bg-gray-800',
        'dark:text-white',
        'rounded-t-md',
        'focus:border-theme-600',
        'focus:ring-1',
        'focus:ring-theme-700',
        'focus:outline-none',
    );
    // Add input to dropdown
    dropdown.appendChild(input);

    // Add options to dropdown
    const optionsContainer = document.createElement('div');
    optionsContainer.classList.add(
        'overflow-y-auto',
        'max-h-64',

    );
    Array.from(select.options).forEach(option => {
        const optionDiv = document.createElement('div');
        optionDiv.textContent = option.text;
        optionDiv.dataset.value = option.value;
        optionDiv.classList.add(
            'p-2',
            'hover:bg-gray-100',
            'dark:hover:bg-gray-700',
            'cursor-pointer',
            'text-gray-800',
            'dark:text-gray-300'
        );
        optionsContainer.appendChild(optionDiv);
    });
    dropdown.appendChild(optionsContainer);

    // Append card and dropdown to the wrapper
    wrapper.appendChild(card);
    wrapper.appendChild(dropdown);

    // Insert the wrapper into the DOM
    select.parentNode.insertBefore(wrapper, select.nextSibling);
    // select.style.display = 'none'; // Hide the original select
    select.style.position = 'absolute';
    // select.style.width = '100px';
    select.style.opacity = '0';
    select.style.pointerEvents = 'none';



    // Toggle dropdown on card click
    card.addEventListener('click', () => {
        if (!select.hasAttribute('readonly')) {
            dropdown.classList.toggle('hidden');
            input.focus();
        }
    });

    // Filter options on input
    input.addEventListener('input', () => {
        const filter = input.value.toLowerCase();
        Array.from(optionsContainer.children).forEach(optionDiv => {
            optionDiv.classList.toggle('hidden', !optionDiv.textContent.toLowerCase().includes(filter));
        });
    });

    // Handle option selection
    optionsContainer.addEventListener('click', event => {
        if (event.target.dataset) {
            select.value = event.target.dataset.value;
            // Manually trigger the change event
            const eventSelect = new Event('change', { bubbles: true });
            select.dispatchEvent(eventSelect);

            card.querySelector('.selected-option').textContent = event.target.textContent;
            dropdown.classList.add('hidden');
        }
    });

    // Close dropdown on outside click
    document.addEventListener('click', event => {
        if (!wrapper.contains(event.target)) {
            dropdown.classList.add('hidden');
        }
    });


    // Add if the select value change the wrapper change too
    select.addEventListener('change', () => {
        // console.log('change');
        card.querySelector('.selected-option').textContent = select.options[select.selectedIndex]?.text || 'Select an option';
    });
}

up.compiler('#navbar-database-selection select', function (select) {
    handleNewSelectElement(select);
})

// Set up a MutationObserver
const observer = new MutationObserver((mutationsList) => {
    for (const mutation of mutationsList) {
        if (mutation.type === 'childList') {
            // Check added nodes
            mutation.addedNodes.forEach((node) => {
                // If it's a <select> element
                if (node.nodeType === 1 && node.tagName.toLowerCase() === 'select') {
                    handleNewSelectElement(node)
                }

                // If a container with nested <select> elements
                if (node.nodeType === 1) {
                    const nestedSelects = node.querySelectorAll('select');
                    nestedSelects.forEach((nestedSelect) => handleNewSelectElement(nestedSelect));
                }
            });
        }
    }
});

// Start observing the document body for changes
observer.observe(document.body, { childList: true, subtree: true });




// Reload the page for special case
up.compiler('.just-updated', function (update) {
    // If the page url has "PaymentRecord"
    if (window.location.href.includes('PaymentRecord')) {
        // Click the search button "search-button"
        document.getElementById('search-button').click();
        // console.log('update');
    }
});


up.compiler('#id_image1', function (image) {
    image.addEventListener('change', function (event) {
        const uploadedFile = event.target.files[0];
        if (uploadedFile) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const imageUrl = e.target.result;
                document.querySelector('.modal-image1 img').src = imageUrl;
            };
            reader.readAsDataURL(uploadedFile);
        }
    });
});
up.compiler('#id_image2', function (image) {
    image.addEventListener('change', function (event) {
        const uploadedFile = event.target.files[0];
        if (uploadedFile) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const imageUrl = e.target.result;
                document.querySelector('.modal-image2 img').src = imageUrl;
            };
            reader.readAsDataURL(uploadedFile);
        }
    });
});



// When a cell in a table is click this function is call, 
// this function will filter row which has the cell value is the cell value of the cell which is clicked
function filterTable(cell, filterText) {
    const table = cell.closest('table');
    const filterValue = cell.textContent.trim();

    const row = cell.closest('tr');
    const cells = Array.from(row.children); // Convert to array to use indexOf
    const columnIndex = cells.indexOf(cell.closest('td')); // Get the column index

    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const display = cells[columnIndex].textContent.includes(filterValue);
        row.style.display = display ? '' : 'none';
    });
    document.getElementById('current-filter-text').innerText = 'Đang lọc: ' + filterText;
    document.getElementById('current-filter').classList.remove('hidden');
}

function totalRequestedAmountDisplay(sum) {
    console.log("Tổng tiền đề nghị: " + sum);
        // humanize sum
        sum = formatNumber(sum);
        // Display the sum in this innerText
        const extraInfoElement = document.getElementById('extra-info')
        if (extraInfoElement) {
            extraInfoElement.innerHTML = `Tổng tiền đề nghị: ${sum} VNĐ`;
        }
    };




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
        // console.log('ConstructionReportPL');
        // Checek if the table contennt changes => call calculatePLTotals
        const observer = new MutationObserver((mutationsList) => {
            for (const mutation of mutationsList) {
                if (mutation.type === 'childList') {
                    calculatePLTotals();
                    calculatePLTotalsToolbar();
                }
            }
        });
        observer.observe(table, { childList: true, subtree: true });
    }

})



up.compiler('#display-table-records', function (table) {
    const currentUrl = window.location.href;
    if (currentUrl.includes('ConstructionReportPL') || currentUrl.includes('vehicle_revenue')) {
        // Calculate totals initially
        calculatePLTotals();

        // Set up observer to recalculate when table content changes
        const observer = new MutationObserver((mutationsList) => {
            for (const mutation of mutationsList) {
                if (mutation.type === 'childList') {
                    calculatePLTotals();
                }
            }
        });
        observer.observe(table, { childList: true, subtree: true });
    }
});


function adjustDisplayRecordsHeight() {
    const displayRecords = document.getElementById("display-records");
    const currentDisplayRecordsHeight = displayRecords.offsetHeight;
    if (currentDisplayRecordsHeight == 0) return false;

    const bodyHeight = document.body.offsetHeight;
    const viewportHeight = window.innerHeight;

    const bottomMargin = 40;
    let newDisplayRecordsHeight = currentDisplayRecordsHeight - (bodyHeight - viewportHeight);
    displayRecords.style.height = `${newDisplayRecordsHeight - bottomMargin}px`;
}


up.compiler('#display-records', function (display) {
    adjustDisplayRecordsHeight();
    // Delay 1 second
    setTimeout(function () {
        adjustDisplayRecordsHeight();
        // load-more opacity = 100
        document.getElementById('load-more').classList.remove('opacity-0');
        document.getElementById('load-more').classList.add('opacity-100');
    }, 1);
});
window.addEventListener("resize", adjustDisplayRecordsHeight);


up.compiler('button[type="submit"]', function (button) {
    button.addEventListener('click', function (e) {
        const form = button.closest('form'); // Find the form containing the button

        if (!form.checkValidity()) {
            form.reportValidity(); // Show validation errors
            return; // Stop execution, don't disable the button
        }

        if (this.classList.contains('disabled')) {
            e.preventDefault();
            return;
        }

        // Store original text in attribute if not already stored
        if (!this.getAttribute('original-text')) {
            this.setAttribute('original-text', this.innerHTML);
        }

        this.classList.add('disabled');
        this.style.opacity = '0.5';
        this.innerHTML = 'Đang xử lý...';



    });
});



up.compiler('#modal-message', function (el) {
    // revert all button submit "Đang xử lý ..." to normal function
    enableSubmitButton();
});

function enableSubmitButton() {
    const buttons = document.querySelectorAll('button[type="submit"]');
    buttons.forEach(button => {
        button.classList.remove('disabled');
        button.style.opacity = '1';
        // Use saved original text from attribute
        button.innerHTML = button.getAttribute('original-text') || 'Xác nhận';
    });
}


function downloadPLTableAsExcel() {
    const table = document.getElementById('display-table-records');
    const wb = XLSX.utils.book_new();
    
    // Prepare the data array
    const data = [];
    
    // Get both header rows
    const headerRows = table.querySelectorAll('thead tr');
    
    // First row - handle colspan and rowspan
    const firstRow = [];
    headerRows[0].querySelectorAll('th').forEach(th => {
        const colspan = th.getAttribute('colspan') || 1;
        const rowspan = th.getAttribute('rowspan') || 1;
        const text = th.textContent.trim();
        
        // If rowspan is 2, add to first row only
        if (rowspan === '2') {
            firstRow.push(text);
        } 
        // If colspan is > 1, repeat the header
        else if (colspan > 1) {
            for (let i = 0; i < colspan; i++) {
                firstRow.push(text);
            }
        }
        // Normal cell
        else {
            firstRow.push(text);
        }
    });
    data.push(firstRow);
    
    // Second row - align with first row structure
    const secondRow = Array(firstRow.length).fill('');
    let currentIndex = 0;
    headerRows[0].querySelectorAll('th').forEach(th => {
        const rowspan = th.getAttribute('rowspan') || 1;
        if (rowspan === '2') {
            currentIndex++;
        }
    });
    
    headerRows[1].querySelectorAll('th').forEach(th => {
        secondRow[currentIndex] = th.textContent.trim();
        currentIndex++;
    });
    data.push(secondRow);
    
    // Get data rows
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const rowData = Array.from(row.querySelectorAll('td')).map(cell => cell.textContent.trim());
        if (rowData.length > 1) { // Skip loading rows
            data.push(rowData);
        }
    });
    
    // Get footer
    const footerRow = table.querySelector('tfoot tr');
    if (footerRow) {
        const footerData = Array.from(footerRow.querySelectorAll('td')).map(cell => cell.textContent.trim());
        data.push(footerData);
    }
    
    // Create worksheet
    const ws = XLSX.utils.aoa_to_sheet(data);
    
    // Set column widths and styles
    const colWidths = firstRow.map(() => ({ wch: 15 }));
    ws['!cols'] = colWidths;
    
    // Merge cells for headers with colspan and rowspan
    ws['!merges'] = [];
    let colIndex = 0;
    headerRows[0].querySelectorAll('th').forEach(th => {
        const colspan = parseInt(th.getAttribute('colspan') || 1);
        const rowspan = parseInt(th.getAttribute('rowspan') || 1);
        
        if (colspan > 1 || rowspan > 1) {
            ws['!merges'].push({
                s: { r: 0, c: colIndex },
                e: { r: rowspan - 1, c: colIndex + colspan - 1 }
            });
        }
        colIndex += colspan;
    });
    
    // Add worksheet to workbook
    XLSX.utils.book_append_sheet(wb, ws, "Báo cáo doanh thu");
    
    // Get current date for filename
    const today = new Date();
    const date = today.getFullYear() + '-' + (today.getMonth() + 1) + '-' + today.getDate();
    
    // Download the file
    XLSX.writeFile(wb, `Bao-cao-P&L-${date}.xlsx`);
}