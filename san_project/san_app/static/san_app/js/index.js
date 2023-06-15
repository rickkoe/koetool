const container = document.getElementById('hot');
const settings = {
  licenseKey: 'non-commercial-and-evaluation',  
  data: [],
  rowHeaders: true,
  colHeaders: ['ID', 'Alias Name', 'WWPN', 'Use'],
  contextMenu: true,
  columns: [
    {data: 'id', readOnly: true},  
    {data: 'alias_name'},
    {data: 'wwpn'},
    {data: 'use'}
  ],
  afterChange: function (changes, source) {
    // Handle changes here
  }
};

const hot = new Handsontable(container, settings);