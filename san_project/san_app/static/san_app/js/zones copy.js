'use strict';

$.ajaxSetup({
    headers: { "X-CSRFToken": getCookie("csrftoken") }
});

$(document).ready(function() {
    let container = document.getElementById('zoneTable');
    let zoneTable;
    const fabricSelectOptions = [];
    const fabricData = [];

    // Define the common options for checkbox columns
    const checkboxColumnOptions = {
        type: "checkbox",
        className: "htCenter"
    };

    // Fetch fabric data from the server
    $.ajax({
        url: '/fabrics_data/',
        type: 'GET',
        dataType: 'json',
        success: function(fabricData) {
            // Populate the fabricSelectOptions array with fabric names and IDs
            fabricData.forEach(function(fabric) {
                fabricSelectOptions.push({
                    label: fabric.name,
                });
            });

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
            ];

            // Add checkbox columns dynamically
            for (let i = 1; i <= 20; i++) {
                columns.push({ data: `member${i}` }, checkboxColumnOptions);
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
                colHeaders: ["ID", "zone Name", "Fabric", "Zone Type", "Create", "Exists", ...Array.from({length: 20}, (_, i) => `Member${i+1}`)],
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
                beforeChange: function(changes) {
                    changes.forEach(function(change) {
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
                            console.log(value)
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
        }
    });

    $('#submit-data').click(function() {
        zoneTable.getPlugin('Filters').clearConditions();
        zoneTable.getPlugin('Filters').filter();
        zoneTable.render();
        let data = zoneTable.getData().map(function(row) {
            if (row[1] || row[2] || row[3] || row[4]) {
                return {
                    id: row[0],
                    name: row[1],
                    wwpn: row[2],
                    use: row[3],
                    fabric: row[4],
                    storage: row[5],
                    create: row[6],
                    include_in_zoning: row[7]
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

    function topFunction() {
        zoneTable.scrollViewportTo(0, 0);
    }
});
