'use strict';

let zoneTable;
const fabricSelectOptions = [];
const aliasSelectOptions = [];
const fabricData = [];
const aliasData = [];

// Define a function to get used aliases for the entire table
function getUsedAliasesForTable(data) {
    let usedAliases = new Set();
    data.forEach(function (row) {
        for (let i = 0; i <= 20; i++) {
            const memberIndex = 5 + i;
            const memberValue = row.members[i];
            // console.log(memberValue);
            if (memberValue !== undefined && memberValue !== null && memberValue !== '') {
                usedAliases.add(memberValue);
            }
        }
    });
    return usedAliases;
}

$(document).ready(function () {
    let container = document.getElementById('zoneTable');

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

    // Fetch alias data from the server
    $.ajax({
        url: '/alias_data/',
        type: 'GET',
        dataType: 'json',
        success: function (aliasData) {
            for (let i = 0; i < aliasData.length; i++) {
                if (aliasData[i].include_in_zoning === true) {
                    aliasSelectOptions.push({
                        label: aliasData[i].name,
                        value: aliasData[i].id,
                        fabric: aliasData[i].fabric
                    });                   
                }
            }
        }
    });


    // Define the columns array dynamically
    const columns = [
        { data: 'id', readOnly: true },
        { data: 'name' },
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
    ];

    for (let i = 1; i <= 20; i++) {
        (function (i) {
            columns.push({
                data: `members.${i - 1}`,
                type: 'dropdown',
                source: function (query, process) {
                    let rowData = this.instance.getDataAtRowProp(this.row, 'fabric__name');
                    let fabricName = rowData; // Assuming 'fabric__name' is the key for fabric in your row data
                    let usedAliases = getUsedAliasesForTable(data);
                    let usedAliasesArray = Array.from(usedAliases);
                    let filteredOptions = aliasSelectOptions.filter(function (alias) {
                        return alias.fabric === fabricName && !usedAliases.has(alias.label);
                    });
                    process(filteredOptions.map(function (alias) {
                        return alias.label;
                    }));
                },
                trimDropdown: false,
            });
        })(i);
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
        colHeaders: ["ID", "Zone Name", "Fabric", "Zone Type", "Create", "Exists", ...Array.from({ length: 20 }, (_, i) => `Member${i + 1}`)],
        contextMenu: ['row_above', 'row_below', 'remove_row', '---------', 'undo', 'redo'],
        minSpareRows: 1,
        manualColumnResize: true,
        cells: function (row, col, prop) {
            if (col === 0) {
                return { readOnly: true };
            }
        },
        columns: columns,
        filters: true,
        dropdownMenu: true,
        afterBeginEditing: function (row, col, prop, value, cellProperties) {
            if (prop === 'fabric__name') {
                let fabric = fabricSelectOptions.find(function (option) {
                    return option.value === value;
                });
                if (fabric) {
                    zoneTable.setDataAtCell(row, col, fabric.label);
                }
            }
        },
        afterChange: function (changes, source) {
            if (source === 'edit') {
                changes.forEach(function (change) {
                    let row = change[0];
                    let prop = change[1];
                    let value = change[3];
                    if (prop === 'fabric__name') {
                        let fabricOption = fabricSelectOptions.find(function (option) {
                            return option.label === value;
                        });
                        if (fabricOption) {
                            data[row].fabric__name = fabricOption.label;
                            data[row].fabric = fabricOption.value;
                        } else if (prop.startsWith('members.')) {
                            const index = parseInt(prop.split('.')[1]) - 1;
                            data[row].members[index] = newValue;
                        }
                    }
                });
            }
        },
    });

    $('#submit-data').click(function () {
        zoneTable.getPlugin('Filters').clearConditions();
        zoneTable.getPlugin('Filters').filter();
        zoneTable.render();
        let data = zoneTable.getData().map(function (row) {
            if (row[1] || row[2] || row[3] || row[4]) {
                let rowData = {
                    id: row[0],
                    name: row[1],
                    fabric: row[2],
                    zone_type: row[3],
                    create: row[4],
                    exists: row[5],
                    members: []
                };
    
                // Extract members data from the appropriate cells
                for (let i = 1; i <= 20; i++) {
                    const memberIndex = 5 + i;
                    const memberValue = row[memberIndex]; 
                    if (memberValue !== undefined) {
                        rowData.members.push(memberValue);
                    }
                }
                return rowData;
            }
        });
    
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
    
});
