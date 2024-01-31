'use strict';

let zoneTable;
const fabricSelectOptions = [];
const aliasSelectOptions = [];
const fabricData = [];

function getTextWidth(text) {
    let canvas = document.createElement('canvas');
    let context = canvas.getContext('2d');
    context.font = '12px Arial'; // Customize the font and size as needed
    let metrics = context.measureText(text);
    return metrics.width;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function() {
    let container = document.getElementById('zoneTable');

    // Fetch fabric data from the server
    $.ajax({
        url: '/fabrics_data/', // Replace with the appropriate URL to fetch fabric data
        type: 'GET',
        dataType: 'json',
        success: function(fabricData) {
            // Populate the fabricSelectOptions array with fabric names and IDs
            for (let i = 0; i < fabricData.length; i++) {
                fabricSelectOptions.push({
                    label: fabricData[i].name,
                });
            }

            // Fetch alias data from the server
            $.ajax({
                url: '/alias_data/',
                type: 'GET',
                dataType: 'json',
                success: function(aliasData) {
                    for (let i = 0; i < aliasData.length; i++) {
                        aliasSelectOptions.push({
                            label: aliasData[i].name,
                        });
                    }

                    // Define the columns array dynamically
                    const columns = [
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
                                    let fabric = fabricSelectOptions.find(function(fabric) {
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
                            type: 'dropdown',
                            source: ['smart_peer', 'standard'],
                            data: 'zone_type' 
                        },
                        {   data: 'create',
                            type: "checkbox",
                            className: "htCenter"
                        },
                        {   data: 'exists',
                        type: "checkbox",
                        className: "htCenter"
                    },
                    ];


                    // Add member columns dynamically
                    for (let i = 1; i <= 20; i++) {
                        // Add data and checkbox columns together
                        columns.push(
                            {   data: `member${i}`,
                                type: 'dropdown',
                                source: function(query, process) {
                                    process(aliasSelectOptions.map(function(alias) {
                                        return alias.label;
                                    }));
                                },
                                renderer: function(instance, td, row, col, prop, value, cellProperties) {
                                    Handsontable.renderers.TextRenderer.apply(this, arguments);
                                    if (prop === "alias__name" && value !== null){
                                        let alias = aliasSelectOptions.find(function(alias) {
                                            return alias.label === value;
                                        });
                                        if (alias) {
                                            td.innerHTML = alias.label;
                                        }
                                    }
                                },
                                trimDropdown: false
                            },
                        );
                    }

                    // Add the columns to the Handsontable configuration
                    zoneTable = new Handsontable(container, {
                        licenseKey: 'non-commercial-and-evaluation',
                        data: typeof data === 'undefined' || data.length === 0 ? [[]] : data,
                        minRows: 1,
                        minCols: 26,
                        rowHeaders: false,
                        width: '100%',
                        height: 600,
                        dragToScroll: true,
                        colHeaders: ["ID", "Zone Name", "Fabric", "Zone Type", "Create", "Exists", ...Array.from({length: 20}, (_, i) => `Member${i+1}`)],
                        contextMenu: ['row_above', 'row_below', 'remove_row', '---------', 'undo', 'redo'],
                        minSpareRows: 1,
                        manualColumnResize: true,
                        cells: function(row, col, prop) {
                            if (col === 0) {
                                return {readOnly: true};
                            }
                        },
                        columns: columns,
                        filters: true,
                        dropdownMenu: true,
                        afterBeginEditing: function(row, col, prop, value, cellProperties) {
                            if (prop === 'fabric__name') {
                                let fabric = fabricSelectOptions.find(function(option) {
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
                                    let row = change[0];
                                    let prop = change[1];
                                    let value = change[3];
                                    if (prop === 'fabric__name') {
                                        let fabricOption = fabricSelectOptions.find(function(option) {
                                            return option.label === value;
                                        });
                                        if (fabricOption) {
                                            data[row].fabric__name = fabricOption.label;
                                            data[row].fabric = fabricOption.value;
                                        }
                                    }
                                });
                            }
                        },
                    });
                } // <- This is the added closing bracket
            }); // <- This is the added closing bracket
        } // <- This is the existing closing bracket
    }); // <- This is the existing closing bracket

    $('#submit-data').click(function() {
        zoneTable.getPlugin('Filters').clearConditions();
        zoneTable.getPlugin('Filters').filter();
        zoneTable.render();
        let data = zoneTable.getData().map(function(row) {
            if (row[1] || row[2] || row[3] || row[4]) {
                return {
                    id: row[0],
                    name: row[1],
                    fabric: row[2],
                    zone_type: row[3],
                    create: row[4],
                    exists: row[5],
                    member1: row[6],
                };
            }
        });

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

    // Function to scroll to the top of the Handsontable
    function topFunction() {
        zoneTable.scrollViewportTo(0, 0);
    }
});
