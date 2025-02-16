
function updateUrlParams(currentUrl, paramsToUpdate) {
    console.log("Current URL:", currentUrl);
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
    console.log("New URL:", newUrl);
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
    console.log(storedTheme);
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
    if (select.options.length <= 6 && !select.hasAttribute('readonly')) {
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
    select.style.display = 'none'; // Hide the original select

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
        console.log('change');
        card.querySelector('.selected-option').textContent = select.options[select.selectedIndex]?.text || 'Select an option';
    });
}



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
        console.log('update');
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

    // Process for table PaymentRecord
    totalRequestedAmountDisplay();
}

function totalRequestedAmountDisplay() {
    const table = document.getElementById('display-table-records');
    const headerRow = table.querySelector('thead tr');
    const requestedAmountColumn = Array.from(headerRow.children).find(th => th.textContent.trim() === "Số tiền đề nghị");
    const requestedAmountIndex = requestedAmountColumn ? Array.from(headerRow.children).indexOf(requestedAmountColumn) : -1;
    if (requestedAmountIndex !== -1) {
        // Get all rows in <tbody>
        const rows = table.querySelectorAll('tbody tr');
        // Calculate sum of the values in that column
        let sum = 0;
        rows.forEach(row => {
            if (row.style.display !== "none") { // Only sum rows that are visible
                const cell = row.children[requestedAmountIndex];
                if (cell) {
                    const value = parseFloat(cell.textContent.replace(/[^0-9.-]+/g, '')); // Remove non-numeric characters
                    if (!isNaN(value)) {
                        sum += value;
                    }
                }
            }
        });
        // humanize sum
        sum = formatNumber(sum);
        // Display the sum in this innerText
        const extraInfoElement = document.getElementById('extra-info')
        if (extraInfoElement) {
            extraInfoElement.innerHTML = `Tổng tiền đề nghị: ${sum} VNĐ`;
        } 
    };
};

up.compiler('#display-table-records', function (table) {
    const headerRow = table.querySelector('thead tr');
    const requestedAmountColumn = Array.from(headerRow.children).find(th => th.textContent.trim() === "Số tiền đề nghị");
    if (requestedAmountColumn) {
        totalRequestedAmountDisplay();
    }
})



function calculatePLTotals() {
    const table = document.getElementById('display-table-records');
    if (!table) return false;
    const headerRow = table.querySelector('thead tr');
    const revenueColumn = Array.from(headerRow.children).find(th => th.textContent.trim() === "Doanh thu");
    const revenueIndex = revenueColumn ? Array.from(headerRow.children).indexOf(revenueColumn) : -1;
    const interestColumn = Array.from(headerRow.children).find(th => th.textContent.trim() === "Lợi nhuận");
    const interestIndex = 13;

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
    if (totalInterest < 0) {
        totalInterestElement.classList.add('text-red-700');
        totalInterestElement.classList.add('bg-red-100');
    }
    // humanize sum
    totalRevenue = formatNumber(totalRevenue);
    totalInterest = formatNumber(totalInterest);
    // Display the sum in this innerText
    const totalRevenueElement = document.getElementById('total-revenue')
    const totalCostElement = document.getElementById('total-cost')
    const totalInterestElement = document.getElementById('total-interest')
    totalRevenueElement.innerHTML = `Tổng doanh thu: ${totalRevenue} VNĐ`;
    totalInterestElement.innerHTML = `Tổng lợi nhuận: ${totalInterest} VNĐ`;

};


up.compiler('#display-table-records', function (table) {
    const currentUrl = window.location.href;
    if (currentUrl.includes('ConstructionReportPL')) {
        console.log('ConstructionReportPL');
        // Checek if the table contennt changes => call calculatePLTotals
        const observer = new MutationObserver((mutationsList) => {
            for (const mutation of mutationsList) {
                if (mutation.type === 'childList') {
                    calculatePLTotals();
                }
            }
        });
        observer.observe(table, { childList: true, subtree: true });
    }

})
