'use strict';
$.ajaxSetup({
    headers: { "X-CSRFToken": getCookie("csrftoken") }
});

let aliasTable;
const fabricSelectOptions = [];
const storageSelectOptions = [];
const hostSelectOptions = [];
const fabricData = [];
const storageData = [];
const hostData = [];
console.log(window.innerHeight);

$(document).ready(function () {
    let container = document.getElementById('aliasTable');
    // Function to calculate viewport height
    function calculateViewportHeight() {
        console.log(window.innerHeight);
        return window.innerHeight;
    }

    // Set the height of the container dynamically
    function setContainerHeight() {
        container.style.height = calculateViewportHeight() + 'px';
    }


    // Call setContainerHeight initially and whenever the window is resized
    setContainerHeight();
    window.addEventListener('resize', setContainerHeight);

    // Check if data array is empty and add an empty row if necessary
    if (typeof data === 'undefined' || data.length === 0) {
        data = [[]];
    }
    // Fetch fabric data from the server
    $.ajax({
        url: '/fabrics_data/', // Replace with the appropriate URL to fetch fabric data
        type: 'GET',
        dataType: 'json',
        success: function (fabricData) {
            // Populate the fabricSelectOptions array with fabric names and IDs
            for (let i = 0; i < fabricData.length; i++) {
                fabricSelectOptions.push({
                    label: fabricData[i].name,
                });
            }
        }
    });
    $.ajax({
        url: '/storage_data/', // Replace with the appropriate URL to fetch fabric data
        type: 'GET',
        dataType: 'json',
        success: function (storageData) {
            // Populate the storageSelectOptions array with fabric names and IDs
            for (let i = 0; i < storageData.length; i++) {
                storageSelectOptions.push({
                    label: storageData[i].name,
                });
            }
        }
    });
    $.ajax({
        url: '/host_data/', // Replace with the appropriate URL to fetch fabric data
        type: 'GET',
        dataType: 'json',
        success: function (hostData) {
            // Populate the hostSelectOptions array with fabric names and IDs
            for (let i = 0; i < hostData.length; i++) {
                hostSelectOptions.push({
                    label: hostData[i].name,
                });
            }
        }
    });

    aliasTable = new Handsontable(container, {
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
        colHeaders: ["ID", "Alias Name", "wwpn", "Use", "Fabric", "Storage", "Host", "Create", "Zone"],
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
            { data: 'name' },
            { data: 'wwpn' },
            {
                type: 'dropdown',
                // editor: 'select',
                source: ['init', 'target', 'both'],
                data: 'use'
            },
            {
                data: 'fabric__name',
                type: 'dropdown',
                source: function (query, process) {
                    process(fabricSelectOptions.map(function (fabric) {
                        return fabric.label;
                    }));
                },
                renderer: function (instance, td, row, col, prop, value, cellProperties) {
                    Handsontable.renderers.TextRenderer.apply(this, arguments);
                    if (prop === "fabric__name" && value !== null) {
                        let fabric = fabricSelectOptions.find(function (fabric) {
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
                type: 'dropdown',
                source: function (query, process) {
                    process(storageSelectOptions.map(function (storage) {
                        return storage.label;
                    }));
                },
                renderer: function (instance, td, row, col, prop, value, cellProperties) {
                    Handsontable.renderers.TextRenderer.apply(this, arguments);
                    if (prop === "storage__name" && value !== null) {
                        let storage = storageSelectOptions.find(function (storage) {
                            return storage.label === value;
                        });
                        if (storage) {
                            td.innerHTML = storage.label;
                        }
                    }
                },
                trimDropdown: false
            },
            {
                data: 'host__name',
                type: 'dropdown',
                source: function (query, process) {
                    process(hostSelectOptions.map(function (host) {
                        return host.label;
                    }));
                },
                renderer: function (instance, td, row, col, prop, value, cellProperties) {
                    Handsontable.renderers.TextRenderer.apply(this, arguments);
                    if (prop === "host__name" && value !== null) {
                        let host = hostSelectOptions.find(function (host) {
                            //   console.log(td, row, rop, value)
                            return host.label === value;
                        });
                        if (host) {
                            td.innerHTML = host.label;
                        }
                    }
                },
                trimDropdown: false
            },
            {
                data: 'create',
                type: "checkbox",
                className: "htCenter"
            },
            {
                data: 'include_in_zoning',
                type: "checkbox",
                className: "htCenter"
            },



        ],
        filters: true,
        dropdownMenu: true,

        beforeChange: function (changes) {
            changes.forEach(function (change) {
                if (change[1] === 'wwpn') {  // If the change is in the 'wwpn' column
                    let newValue = change[3];
                    if (/^[0-9a-fA-F]{16}$/.test(newValue)) {  // If it's 16 hexadecimal characters without colons
                        change[3] = newValue.replace(/(.{2})(?=.)/g, '$1:');  // Insert colons
                    } else if (!/^([0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}$/.test(newValue)) {  // If it's not 16 hexadecimal characters with colons
                        change[3] = null;  // Discard the change
                        alert('Invalid wwpn format!');
                    }
                }
            });
        },
        afterBeginEditing: function (row, col, prop, value, cellProperties) {
            if (prop === 'fabric__name') {
                let fabric = fabricSelectOptions.find(function (option) {
                    return option.value === value;
                });

                if (fabric) {
                    aliasTable.setDataAtCell(row, col, fabric.label);
                }
            }
        },
        afterChange: function (changes, source) {
            if (source === 'edit') {
                changes.forEach(function (change) {
                    let row = change[0];
                    let prop = change[1];
                    let value = change[3];
                    console.log(value)
                    if (prop === 'fabric__name') {
                        let fabricOption = fabricSelectOptions.find(function (option) {
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
    );



$('#submit-data').click(function () {
    aliasTable.getPlugin('Filters').clearConditions();
    aliasTable.getPlugin('Filters').filter();
    aliasTable.render();
    let data = aliasTable.getData().map(function (row) {
        console.log(row);
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
