// import Handsontable from 'handsontable';
// import 'handsontable/plugins/filters/filters';


$.ajaxSetup({
  headers: { "X-CSRFToken": getCookie("csrftoken") }
});

var aliasTable;

$(document).ready(function() {
    var container = document.getElementById('aliasTable');
    console.log(typeof data);  // Outputs: "object" because in JavaScript, arrays are technically a type of object
    console.log(data.length)
      // Check if data array is empty and add an empty row if necessary

      if (typeof data === 'undefined' || data.length == 0) {
        data = [[]];
    }
    // console.log(typeof data);  // Outputs: "object" because in JavaScript, arrays are technically a type of object
    console.log(data.length)
    aliasTable = new Handsontable(container, {
        licenseKey: 'non-commercial-and-evaluation',
        data: data,
        minRows: 5,
        minCols: 4,
        rowHeaders: true,
        colHeaders: ["ID", "Alias Name", "WWPN", "Use"],
        contextMenu: ['row_above', 'row_below', 'remove_row', '---------', 'undo', 'redo'],  // Custom context menu options
        minSpareRows: 1,  // Always leave one spare row at the end
        // Disable ID column
        cells: function(row, col, prop) {
            if (col === 0) {
                return {readOnly: true};
            }
        },
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
        }
    });
  });
  
   
  $('#submit-data').click(function() {
    var data = aliasTable.getData().map(function(row) {
        if (row[1] || row[2] || row[3]) {  // Only send rows that have at least one of these fields filled
            return {
                id: row[0],
                alias_name: row[1],
                WWPN: row[2],
                use: row[3]
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
          var cookie = jQuery.trim(cookies[i]);
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}