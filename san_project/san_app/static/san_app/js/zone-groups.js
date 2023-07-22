// import 'handsontable/dist/handsontable.full.min.css';
// import Handsontable from 'handsontable/base';
// import { registerAllModules } from 'handsontable/registry';

// registerAllModules();




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
                });
            }

            zoneTable = new Handsontable(container, {
                licenseKey: 'non-commercial-and-evaluation',
                data: data,
                minRows: 1,
                minCols: 6,
                rowHeaders: false,
                width: '100%',
                height: 600,
     

                // when selection reaches the edge of the grid's viewport, scroll the viewport
                dragToScroll: true,
                colHeaders: ["ID", "Zone Group Name", "Fabric", "Storage", "Zone Type", "Create", "Exists"],
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
                        data: 'fabric__name',
                        type: 'dropdown',
                        source: function(query, process) {
                          process(fabricSelectOptions.map(function(fabric) {
                            return fabric.label;
                          }));
                        },
                        renderer: function(instance, td, row, col, prop, value, cellProperties) {
                          Handsontable.renderers.TextRenderer.apply(this, arguments);
                          if (prop === "fabric__name" && value !== null){
                            var fabric = fabricSelectOptions.find(function(fabric) {
                            //   console.log(td, row, prop, value)
                              return fabric.label === value;
                            });
                            if (fabric) {
                              td.innerHTML = fabric.label;
                            }
                          }
                        },
                        trimDropdown: false
                    },
                    {
                        data: 'storage__name',
                        // type: 'dropdown',
                        // source: function(query, process) {
                        //   process(storageSelectOptions.map(function(storage) {
                        //     return storage.label;
                        //   }));
                        // },
                        // renderer: function(instance, td, row, col, prop, value, cellProperties) {
                        //   Handsontable.renderers.TextRenderer.apply(this, arguments);
                        //   if (prop === "storage__name" && value !== null){
                        //     var storage = storageSelectOptions.find(function(storage) {
                        //     //   console.log(td, row, prop, value)
                        //       return storage.label === value;
                        //     });
                        //     if (storage) {
                        //       td.innerHTML = storage.label;
                        //     }
                        //   }
                        // },
                        // trimDropdown: false
                    },
                    { 
                        type: 'dropdown',
                        // editor: 'select',
                        source: ['smart', 'standard'],
                        data: 'zone_type' },
                    {
                        data: 'create',
                        type: "checkbox",
                        className: "htCenter"
                      },
                      {
                        data: 'exists',
                        type: "checkbox",
                        className: "htCenter"
                      },
        

                      
                ],
                filters: true,
                dropdownMenu: true,

                beforeChange: function(changes) {
                    changes.forEach(function(change) {
                        if (change[1] === 'wwpn') {  // If the change is in the 'wwpn' column
                            var newValue = change[3];
                            if (/^[0-9a-fA-F]{16}$/.test(newValue)) {  // If it's 16 hexadecimal characters without colons
                                change[3] = newValue.replace(/(.{2})(?=.)/g, '$1:');  // Insert colons
                            } else if (!/^([0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}$/.test(newValue)) {  // If it's not 16 hexadecimal characters with colons
                                change[3] = null;  // Discard the change
                                alert('Invalid wwpn format!');
                            }
                        }
                    });
                },
                afterBeginEditing: function(row, col, prop, value, cellProperties) {
                    if (prop === 'fabric__name') {
                      var fabric = fabricSelectOptions.find(function(option) {
                        return option.value === value;
                      });
                  
                      if (fabric) {
                        zoneTable.setDataAtCell(row, col, fabric.label);
                      }
                    }
                  },                  
                  afterChange: function(changes, source) {
                    if (source === 'edit') {
                        changes.forEach(function(change) {
                            var row = change[0];
                            var prop = change[1];
                            var value = change[3];
                            console.log(value)
                            if (prop === 'fabric__name') {
                                var fabricOption = fabricSelectOptions.find(function(option) {
                                    return option.label === value;
                                });
                
                                if (fabricOption) {
                                    // Assign the fabric ID to the 'fabric__name' property
                                    data[row].fabric__name = fabricOption.label;
                                    data[row].fabric = fabricOption.value; // Assign the fabric name to the 'fabric' property
                                }
                            }
                        });
                    }
                },
                
                
                
            });
        }
    });
});


$('#submit-data').click(function() {
    zoneTable.getPlugin('Filters').clearConditions();
    zoneTable.getPlugin('Filters').filter();
    zoneTable.render();
    var data = zoneTable.getData().map(function(row) {
        if (row[1] || row[2] || row[3] || row[4]) {  // Only send rows that have at least one of these fields filled
            return {
                id: row[0],
                name: row[1],
                fabric: row[2],
                storage: row[3],
                zone_type: row[4],
                create: row[5],
                exists: row[6]
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

// When the user clicks on the button, scroll to the top of the Handsontable
function topFunction() {
    zoneTable.scrollViewportTo(0, 0);
    }  
}
