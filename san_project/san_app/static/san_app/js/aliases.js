'use strict';
$.ajaxSetup({
    headers: { "X-CSRFToken": getCookie("csrftoken") }
});

let aliasTable;
const fabricSelectOptions = [];
const storageSelectOptions = [];
const hostSelectOptions = [];

// Function to get CSRF token from cookies
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

// Function to fetch data and populate dropdown options
function fetchData(url, selectOptions) {
    return $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            for (let i = 0; i < data.length; i++) {
                selectOptions.push({
                    label: data[i].name,
                });
            }
        },
        error: function (xhr, status, error) {
            console.error(`Error fetching data from ${url}:`, error);
        }
    });
}

// Set the height of the container dynamically
function setContainerHeight(container) {
    const viewportHeight = window.innerHeight;
    // console.log(viewportHeight);
    container.style.height = (viewportHeight) + 'px'; // Adjust 100px as per your layout
    // console.log(container.style.height);
}

// Function to initialize Handsontable
function initializeHandsontable(container, data) {
    return new Handsontable(container, {
        className: 'customTable',
        licenseKey: 'non-commercial-and-evaluation',
        data: data,
        minRows: 1,
        minCols: 7,
        rowHeaders: false,
        width: '100%',
        height: '100%',
        columnSorting: true,
        dragToScroll: true,
        colHeaders: ["ID", "Alias Name", "wwpn", "Use", "Fabric", "Storage", "Host", "Create", "Zone"],
        contextMenu: ['row_above', 'row_below', 'remove_row', '---------', 'undo', 'redo'],
        minSpareRows: 1,
        manualColumnResize: true,
        cells: function (row, col, prop) {
            const cellProperties = {};
            cellProperties.className = row % 2 === 0 ? 'darkRow' : 'lightRow';
            if (col === 7 || col === 8) {
                cellProperties.className += ' htCenter';
            }
            return cellProperties;
        },
        columns: [
            { data: 'id', readOnly: true },
            { data: 'name' },
            { data: 'wwpn' },
            {
                type: 'dropdown',
                source: ['init', 'target', 'both'],
                data: 'use'
            },
            {
                data: 'fabric__name',
                type: 'dropdown',
                source: function (query, process) {
                    process(fabricSelectOptions.map(fabric => fabric.label));
                },
                renderer: function (instance, td, row, col, prop, value) {
                    Handsontable.renderers.TextRenderer.apply(this, arguments);
                    if (value !== null) {
                        let fabric = fabricSelectOptions.find(fabric => fabric.label === value);
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
                    process(storageSelectOptions.map(storage => storage.label));
                },
                renderer: function (instance, td, row, col, prop, value) {
                    Handsontable.renderers.TextRenderer.apply(this, arguments);
                    if (value !== null) {
                        let storage = storageSelectOptions.find(storage => storage.label === value);
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
                    process(hostSelectOptions.map(host => host.label));
                },
                renderer: function (instance, td, row, col, prop, value) {
                    Handsontable.renderers.TextRenderer.apply(this, arguments);
                    if (value !== null) {
                        let host = hostSelectOptions.find(host => host.label === value);
                        if (host) {
                            td.innerHTML = host.label;
                        }
                    }
                },
                trimDropdown: false
            },
            { data: 'create', type: "checkbox", className: "htCenter" },
            { data: 'include_in_zoning', type: "checkbox", className: "htCenter" }
        ],
        filters: true,
        dropdownMenu: true,
        beforeChange: function (changes) {
            changes.forEach(function (change) {
                if (change[1] === 'wwpn') {
                    let newValue = change[3];
                    if (/^[0-9a-fA-F]{16}$/.test(newValue)) {
                        change[3] = newValue.replace(/(.{2})(?=.)/g, '$1:');
                    } else if (!/^([0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2}$/.test(newValue)) {
                        change[3] = null;
                        alert('Invalid wwpn format!');
                    }
                }
            });
        },
        afterChange: function (changes, source) {
            if (source === 'edit') {
                changes.forEach(function (change) {
                    let row = change[0];
                    let prop = change[1];
                    let value = change[3];
                    if (prop === 'fabric__name') {
                        let fabricOption = fabricSelectOptions.find(option => option.label === value);
                        if (fabricOption) {
                            data[row].fabric__name = fabricOption.label;
                            data[row].fabric = fabricOption.value;
                        }
                    }
                });
            }
        }
    });
}

// Initialize the table on document ready
$(document).ready(function () {
    let container = document.getElementById('aliasTable');
    let aliasTableContainer = document.getElementById('aliasTableContainer');

    // Set the initial height of the container
    setContainerHeight(aliasTableContainer);
    window.addEventListener('resize', () => setContainerHeight(aliasTableContainer));

    // Initialize table data
    if (typeof data === 'undefined' || data.length === 0) {
        data = [[]];
    }

    // Fetch data for dropdowns
    $.when(
        fetchData('/fabrics_data/', fabricSelectOptions),
        fetchData('/storage_data/', storageSelectOptions),
        fetchData('/host_data/', hostSelectOptions)
    ).then(() => {
        // Initialize Handsontable after data has been fetched
        aliasTable = initializeHandsontable(container, data);
    });

    // Submit data handler
    $('#submit-data').click(function () {
        aliasTable.getPlugin('Filters').clearConditions();
        aliasTable.getPlugin('Filters').filter();
        aliasTable.render();
        let data = aliasTable.getData().map(function (row) {
            if (row[1] || row[2] || row[3] || row[4]) {
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
        }).filter(entry => entry !== undefined);

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
});