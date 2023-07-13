$.ajaxSetup({
    headers: { "X-CSRFToken": getCookie("csrftoken") }
});

var zoneTable;
var fabricSelectOptions = [];
var fabricData = []

function getTextWidth(text) {
    var canvas = document.createElement('canvas');
    var context = canvas.getContext('2d');
    context.font = '12px Arial'; // Customize the font and size as needed
    var metrics = context.measureText(text);
    return metrics.width;
  }
  
  

$(document).ready(function() {
    var container = document.getElementById('zoneTable');


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

            zoneTable = new Handsontable(container, {
                licenseKey: 'non-commercial-and-evaluation',
                data: data,
                minRows: 1,
                minCols: 6,
                rowHeaders: false,
                colHeaders: ["ID", "Zone Name", "Fabric", "Zone Type", "Exists", "Members"],
                contextMenu: ['row_above', 'row_below', 'remove_row', '---------', 'undo', 'redo'],  // Custom context menu options
                minSpareRows: 1,  // Always leave one spare row at the end
                    // Enable column resizing
                manualColumnResize: true,
                // Disable ID column
                cells: function(row, col, prop) {
                    if (col === 0) {
                        return {readOnly: true};
                    }
                },
                columns: [
                    { data: 'id', readOnly: true },
                    { data: 'name' },
                    {
                        data: 'fabric_id',
                        type: 'dropdown',
                        source: function(query, process) {
                          process(fabricSelectOptions.map(function(fabric) {
                            return fabric.label;
                          }));
                        },
                        renderer: function(instance, td, row, col, prop, value, cellProperties) {
                          Handsontable.renderers.AutocompleteRenderer.apply(this, arguments);
                          if (prop === "fabric_id" && value !== null){
                            var fabric = fabricSelectOptions.find(function(fabric) {
                              console.log(td, row, prop, value)
                              return fabric.value === value;
                            });
                            if (fabric) {
                              td.innerHTML = fabric.label;
                            }
                          }
                        },
                        trimDropdown: false
                    },
                    { 
                        type: 'dropdown',
                        editor: 'select',
                        selectOptions: ['smart_peer', 'standard'],
                        data: 'zone_type' },
                    {   
                        type: 'dropdown',
                        editor: 'select',
                        selectOptions: ['True','False'],
                        data: 'exists'
                    },
                    ...memberColumns
  
                ],
                beforeChange: function(changes) {
                    changes.forEach(function(change) {
                        if (change[1] === 'WWPN') {  // If the change is in the 'WWPN' column
                            var newValue = change[3];
                            if (/^[0-9a-fA-F]{16}$/.test(newValue)) {  // If it's 16 hexadecimal characters without colons
                                change[3] = newValue.replace(/(.{2})(?=.)/g, '$1:');  // Insert colons
                            } else if (!/^([0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}$/.test(newValue)) {  // If it's not 16 hexadecimal characters with colons
                                change[3] = null;  // Discard the change
                                alert('Invalid WWPN format!');
                            }
                        }
                    });
                },
                afterChange: function(changes, source) {
                    if (source === 'edit') {
                        // changes is an array with the following fields:
                        // 0 = the row in the table
                        // 1 = the table column that was changed
                        // 2 = the old value
                        // 3 = the new value

                        changes.forEach(function(change) {
                            var row = change[0];
                            var prop = change[1];
                            var value = change[3];
                
                            if (prop === 'fabric_id') {
                                var fabric = fabricSelectOptions.find(function(option) {
                                    return option.label === value;
                                });
                
                                if (fabric) {
                                    data[row].fabric_id = fabric.value;
                                }
                            }
                        });
                    }
                }
                
            });
        }
    });
});


$('#submit-data').click(function() {
    var data = zoneTable.getData().map(function(row) {
        if (row[1] || row[2] || row[3] || row[4]) {  // Only send rows that have at least one of these fields filled
            return {
                id: row[0],
                name: row[1],
                fabric: row[2],
                zone_type: row[3],
                exists: row[4],
                member_list: row[5]
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
        success: function() {
            location.reload();
        },
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