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
up.compiler('#nav_bar', function(element) {

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
        item.addEventListener('click', function() {
            activeMenuItem(item);
        });

        // Check if the item url equals to the current url => active the item
        if (item.getAttribute('href') === window.location.pathname) {
            activeMenuItem(item);
        }
    });
});



// THEME CHANGE =========================================
up.compiler('#theme-toggle', function(element) {
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
up.compiler('.menu', function(element) {
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
    element.querySelector('.menu-button').addEventListener('click', function() {
            showHideMenu(element, 'toggle')
            // Hide all other menus when click to a menu
            document.querySelectorAll('.menu').forEach(menu => {
                if (menu !== element) {
                    showHideMenu(menu, 'hide')
                }
            })
    });

    // Hide menus when clicking outside of them
    document.addEventListener('click', function(event) {
        if (!element.contains(event.target)) {
            showHideMenu(element, 'hide')
        }
    })



});





// RESPONSIVE ELEMENTS ON RESIZE =========================================
up.compiler('.display-cards', function(element) {
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





up.compiler('#record-edit', function(recordEdit) {
    function getClosestRecordElement() {
        let closestRecord = recordEdit.closest('[id*="record_"]');
        closestRecord.addEventListener('dblclick', function() {
            recordEdit.click();
        });
    
    }
    getClosestRecordElement();
});


up.compiler('.expand', function(expand) {
    // Add event listener to the document
    document.addEventListener('click', function(event) {
        // If the target is not the expand element, then remove the style height
        if (event.target !== expand) {
            expand.style.height = '';
        }
    });
    // Add event listener to the document
    document.addEventListener('focus', function(event) {
        // If the target is not the expand element, then remove the style height
        if (event.target !== expand) {
            expand.style.height = '';
        }
    });
    // Add event listener to the expand element
    expand.addEventListener('click', function() {
        // Add style height 100px
        expand.style.height = '150px';
    });
    expand.addEventListener('focus', function() {
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


up.compiler('.form-input', function(inputfield) {
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


    // Create a popup element
    const popup = document.createElement('div');
    popup.classList.add('text-blue-500'); // You can style this with Tailwind or custom CSS


    // Event listener for focus
    inputfield.addEventListener('focus', function() {

        // Initialize the field value if present
         popup.innerText = formatNumber(inputfield.value);

        // Insert the popup after the input field
        inputfield.parentNode.insertBefore(popup, inputfield.nextSibling);
        
        // Optionally, remove the popup on blur or some other event
        inputfield.addEventListener('blur', function() {
            popup.remove();
        });
    });

    // Add keyup event listener to format the value and update tooltip
    inputfield.addEventListener('keyup', function() {
        popup.innerText = formatNumber(inputfield.value);

    });

});
