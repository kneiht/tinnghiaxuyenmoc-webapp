
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
    saveButton.addEventListener('click', function (event) {
        editButton.classList.remove('hidden');
        saveButton.classList.add('hidden');
        addButton.classList.add('hidden');
        cancelButton.classList.add('hidden');
        showDisplay();
    })

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
        newRow.querySelectorAll('input, select').forEach(function (element) {
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

