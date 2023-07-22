$.ajaxSetup({
    headers: { "X-CSRFToken": getCookie("csrftoken") }
});

var fabricTable;
var fabricSelectOptions = [];
var fabricData = [];

function getTextWidth(text) {
    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');
    context.font = '12px Arial'; // Customize the font and size as needed
    var metrics = context.measureText(text);
    return metrics.width;
}

$(document).ready(function() {
    var container = document.getElementById('fabricTable');

    // Check if data array is empty and add an empty row if necessary
    if (typeof data === 'undefined' || data.length === 0) {
        data = [[]];
    }

    // Fetch fabric data from the server
    $.ajax({
        url: '/fabrics_data/', // Replace with the appropriate URL to fetch fabric data
        type: 'GET',
        dataType: 'json',
        success: function(fabricData) {
            // Populate the fabricSelectOptions array with fabric names and IDs
            for (var i = 0; i < fabricData.length; i++) {
                fabricSelectOptions.push({
                    label: fabricData[i].name,
                    value: fabricData[i].id,
                });
            }
            fabricTable = new Handsontable(container, {
                licenseKey: 'non-commercial-and-evaluation',
                data: data,
                minRows: 1,
                minCols: 5,
                rowHeaders: false,
                colHeaders: ["ID", "Name", "Active Zoneset", "VSAN", "Exists"],
                contextMenu: ['row_above', 'row_below', 'remove_row', '---------', 'undo', 'redo'],  // Custom context menu options
                minSpareRows: 1,  // Always leave one spare row at the end
                // Enable column resizing
                manualColumnResize: true,
                // Disable ID column
                cells: function(row, col, prop) {
                    if (col === 0) {
                        return { readOnly: true };
                    }
                },
                columns: [
                    { data: 'id', readOnly: true },
                    { data: 'name' },
                    { data: 'zoneset_name' },
                    { data: 'vsan' },
                    { 
                        data: 'exists',
                        type: 'checkbox',
                        className: "htCenter"
                    }
                ],
            });
        }
    });
});

$('#submit-fabric-data').click(function() {
    var data = fabricTable.getData().map(function(row) {
        if (row[1] || row[2] || row[3] || row[4]) {  // Only send rows that have at least one of these fields filled
            return {
                id: row[0],
                name: row[1],
                zoneset_name: row[2],
                vsan: row[3],
                exists: row[4]
            };
        }
    });

    // Filter out any undefined entries (rows that didn't pass the check)
    data = data.filter(function(entry) { return entry !== undefined; });

    $.ajax({
        type: 'POST',
        url: '',
        data: {
            'data': JSON.stringify(data),
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
        },
        success: function(response) {
            if (response.status === 'success') {
                location.reload();  // Refresh the page on successful submission
            } else if (response.status === 'error') {
                alert(response.errors.join('\n'));  // Display the error message to the user
            }
        },
        error: function(xhr, errmsg, err) {
            console.log('Error:', errmsg);
        }
    });
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
