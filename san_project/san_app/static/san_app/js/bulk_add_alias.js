// Set up AJAX to use Django's CSRF protection
// This is needed because Django's CSRF middleware requires the CSRF token to be included in any POST request
$.ajaxSetup({
    headers: { "X-CSRFToken": getCookie("csrftoken") }
});

// This function will run when the page is ready
$(document).ready(function() {
    // Initial data for Handsontable
    // It's a 2D array representing the table's rows and columns
    var data = [
        ["", "", ""]
    ];

    // Get the DOM element that will contain the Handsontable
    var container = document.getElementById('hot');
    
    // Initialize Handsontable
    var hot = new Handsontable(container, {
        licenseKey: 'non-commercial-and-evaluation',
        data: data,
        minRows: 2,  // Minimum number of rows
        minCols: 3,  // Minimum number of columns
        rowHeaders: true,  // Enable row headers
        colHeaders: ["Alias Name", "WWPN", "Use"],  // Column headers
        contextMenu: ['row_above', 'row_below', 'remove_row', '---------', 'undo', 'redo'],  // Custom context menu options
        minSpareRows: 1,  // Always leave one spare row at the end
    });
    
    // This function will run when the button with the id "submit-data" is clicked
    $('#submit-data').click(function() {
        var data = hot.getData();  // Get the data from Handsontable
        // Send a POST request to the current URL
        $.ajax({
            type: 'POST',
            url: '',
            data: {
                'data': JSON.stringify(data),  // Convert the data to JSON
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),  // Add the CSRF token
            },
            success: function() {
                window.location.href = '/';  // Redirect to the root URL on success
            },
            error: function(error) {
                // This is where you handle the error.
                // In this example, we just alert the error messages.
                var errorMessages = error.responseJSON.error;
                alert("There were errors with your submission: \n" + errorMessages.join("\n"));
            },
        });
    });
});

// This function gets a cookie by name
// It's used by the AJAX setup to get the CSRF token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
