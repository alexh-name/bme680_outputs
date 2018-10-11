var url = 'http://pi.home/cgi-bin/bme.sh';
var entries = 28800;
var ready = false;

var DATEs = [];
var Cs = [];
var IAQs = [];
var TEMPs = [];
var HUMs = [];
var counter = 0;

getCSV(url, entries);
window.setInterval(update, 3000);

function addData(chart, data, set, mode) {
  if (mode == 'move') {
    chart.data.labels.splice(0, 1); // remove first label
    chart.data.datasets[set].data.splice(0, 1); // remove first data point
  }
  chart.data.datasets[set].data.push(data);
}

function addLabel(chart, label, mode) {
  if (mode == 'move') {
    chart.data.labels.splice(0, 1); // remove first label
  } else {
    chart.data.labels.push(label);
  }
}

function assignCSV(str) {
  var array = str.split(',');
  DATEs.push(array[0]);
  Cs.push(array[1] * 100);
  IAQs.push(array[2]);
  TEMPs.push(array[3]);
  HUMs.push(array[4]);
}

function prepareCSV(csv, mode) {
  if (mode == 'multiline') {
    csv = csv.split('\n');
    $.each(csv, function(index, item) {
      if (item != '') {
        assignCSV(item);
      }
    });
  } else {
    assignCSV(csv);
  }
}

function getCSV(url, entries) {
  $.get(url + '?' + entries, function(data, status){
    prepareCSV(data, 'multiline');
    $.each(DATEs, function(index, item) {
      var date = item;
      var C = Cs[index];
      var IAQ = IAQs[index];
      var Temp = TEMPs[index];
      var Hum = HUMs[index];
      var i;
      for (i = 0; i < 1; i++) {
        addLabel(chart, date, 'add');
        addData(chart, C, 3, 'add');
        addData(chart, IAQ, 2, 'add');
        addData(chart, Temp, 0, 'add');
        addData(chart, Hum, 1, 'add');
      } 
    });
    chart.update();
    ready = true;
  });
}

function update() {
  if (ready) {
    $.get(url + '?1', function(data, status){
      counter++;
      prepareCSV(data, 'single');
      var date = DATEs.slice(-1)[0];
      var IAQ = IAQs.slice(-1)[0];
      var C = Cs.slice(-1)[0];
      var Temp = TEMPs.slice(-1)[0];
      var Hum = HUMs.slice(-1)[0];
      var mode = 'add';
      if (counter == 300) {
        mode = 'move';
        counter = 0;
      }
      addLabel(chart, date, mode);
      addData(chart, C, 3, mode);
      addData(chart, IAQ, 2, mode);
      addData(chart, Temp, 0, mode);
      addData(chart, Hum, 1, mode);
      chart.update();
    });
  }
}

