
up.compiler('.transport-table', function (transportTable) {
    var editButton = transportTable.querySelector('#edit');
    var saveButton = transportTable.querySelector('#save');
    var cancelButton = transportTable.querySelector('#cancel');
    var addButton = transportTable.querySelector('#add');
    var inputs = transportTable.querySelectorAll('.input');
    var displays = transportTable.querySelectorAll('.display');



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
        console.log(addRowTemplate);
        // Clone the rowplate and append it to the table    
        var newRow = addRowTemplate.cloneNode(true);
        // Replace the rowplate with the new row
        transportTable.querySelector('table').appendChild(newRow);
        // find all input and select elements in the new row and remove disabled
        newRow.querySelectorAll('input, select, textarea').forEach(function (element) {
            element.removeAttribute('disabled');
        })


        // unhide
        newRow.classList.remove('hidden');
    })


    // Write function find and hide or show element with class display and input
    function showDisplay() {
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
        let databaseSelection = document.getElementById('database-selection');
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
        let databaseSelection = document.getElementById('database-selection');
        let aTags = databaseSelection.querySelectorAll('#driver_salary, #vehicle_avenue');

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