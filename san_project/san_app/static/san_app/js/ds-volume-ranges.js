'use strict';
$.ajaxSetup({
    headers: { "X-CSRFToken": getCookie("csrftoken") }
});

let volumeRangeTable;
const storageSelectOptions = [];
const storageData = [];

$(document).ready(function () {
    let container = document.getElementById('volumeRangeTable');
    // Function to calculate viewport height
    function calculateViewportHeight() {
        return window.innerHeight;
    }


    // Check if data array is empty and add an empty row if necessary
    if (typeof data === 'undefined' || data.length === 0) {
        data = [[]];
    }

    $.ajax({
        url: '/storage_data/', // Replace with the appropriate URL to fetch fabric data
        type: 'GET',
        dataType: 'json',
        success: function (storageData) {
            // Populate the storageSelectOptions array with fabric names and IDs
            for (let i = 0; i < storageData.length; i++) {
                storageSelectOptions.push({
                    label: storageData[i].name,
                    id: storageData[i].id,
                });
            }
        }
    });

    console.log(data);
    volumeRangeTable = new Handsontable(container, {
        // className: 'table table-dark',
        className: 'customTable', 
        licenseKey: 'non-commercial-and-evaluation',
        data: data,
        minRows: 1,
        minCols: 7,
        rowHeaders: false,
        width: '100%',
        height: '100%',
        columnSorting: true,


        // when selection reaches the edge of the grid's viewport, scroll the viewport
        dragToScroll: true,
        colHeaders: ['ID', 'Site', 'LPAR', 'Use', 'Source DS8k', 'Source Pool', 'Source Volume Start', 'Source Volume End', 'Target DS8k', 'Target Volume Start', 'Target Volume End', 'Create'],
        contextMenu: ['row_above', 'row_below', 'remove_row', '---------', 'undo', 'redo'],  // Custom context menu options
        minSpareRows: 1,  // Always leave one spare row at the end
        // Enable column resizing
        manualColumnResize: true,
        // Disable ID column
        cells: function(row, col, prop) {
            const cellProperties = {};
            if(row % 2 === 0) {
                cellProperties.className = 'darkRow';
            } else {
                cellProperties.className = 'lightRow'
            }
            if (col === 7 || col === 8) {
                cellProperties.className = (cellProperties.className || '') + ' htCenter'; // Append to existing classes
            }
            return cellProperties;
        },
        columns: [
            { data: 'id', readOnly: true },
            { data: 'site' },
            { data: 'lpar' },
            { data: 'use' },
            {
                data: 'source_ds8k_id',
                type: 'dropdown',
                source: function (query, process) {
                    process(storageSelectOptions.map(function (storage) {
                        return storage.label;
                    }));
                },
                
                renderer: function (instance, td, row, col, prop, value, cellProperties) {
                    Handsontable.renderers.TextRenderer.apply(this, arguments);
                    if (prop === "source_ds8k_id" && value !== null) {
                        let storage = storageSelectOptions.find(function (storage) {
                            return storage.id === value;
                        });
                        
                        if (storage) {
                            instance.setDataAtCell(row, col, storage.label);
                        }
                    }
                },
                trimDropdown: false
            },
            { data: 'source_pool' },
            { data: 'source_start' },
            { data: 'source_end' },
            {
                data: 'target_ds8k_id',
                type: 'dropdown',
                source: function (query, process) {
                    process(storageSelectOptions.map(function (storage) {
                        return storage.label;
                    }));
                },
                
                renderer: function (instance, td, row, col, prop, value, cellProperties) {
                    Handsontable.renderers.TextRenderer.apply(this, arguments);
                    if (prop === "target_ds8k_id" && value !== null) {
                        let storage = storageSelectOptions.find(function (storage) {
                            return storage.id === value;
                        });
                        
                        if (storage) {
                            instance.setDataAtCell(row, col, storage.label);
                        }
                    }
                },
                trimDropdown: false
            },
            { data: 'target_start' },
            { data: 'target_end' },
            {
                data: 'create',
                type: "checkbox",
                className: "htCenter"
            },
        ],
        filters: true,
        dropdownMenu: true,

    
    });
        }
    );



$('#submit-data').click(function () {
    aliasTable.getPlugin('Filters').clearConditions();
    aliasTable.getPlugin('Filters').filter();
    aliasTable.render();
    let data = aliasTable.getData().map(function (row) {
        if (row[1] || row[2] || row[3] || row[4]) {  // Only send rows that have at least one of these fields filled
            return {
                id: row[0],
                name: row[1],
                wwpn: row[2],
                use: row[3],
                fabric: row[4],
                storage: row[5],
                host: row[6],
                create: row[7],
                include_in_zoning: row[8]
            };
        }
    });

    // Filter out any undefined entries (rows that didn't pass the check)

    data = data.filter(function (entry) { return entry !== undefined; });

    $.ajax({
        type: 'POST',
        url: '',
        data: {
            'data': JSON.stringify(data),
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
        },
        success: function () {
            location.reload();
        },
    });
});

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

    // When the user clicks on the button, scroll to the top of the Handsontable
    function topFunction() {
        aliasTable.scrollViewportTo(0, 0);
    }
}
