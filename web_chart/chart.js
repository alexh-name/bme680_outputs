var ctx = document.getElementById(CHART_ID).getContext('2d');
var chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [
    {
      label: 'Temp',
      data: [],
      backgroundColor: [
        'rgba(255, 99, 132, 0.2)'
      ],
      borderColor: [
        'rgba(255,99,132,1)'
      ]
    },
    {
      label: 'Hum',
      data: [],
      backgroundColor: [
        'rgba(54, 162, 235, 0.2)'
      ],
      borderColor: [
        'rgba(54, 162, 235, 1)'
      ]
    },
    {
      label: 'IAQ',
      data: [],
      backgroundColor: [
        'rgba(75, 192, 192, 0.2)'
      ],
      borderColor: [
        'rgba(75, 192, 192, 1)'
      ]
    },
    {
      label: 'Confidence',
      data: [],
      backgroundColor: [
        'rgba(255, 206, 86, 0.2)'
      ],
      borderColor: [
        'rgba(255, 206, 86, 1)'
      ]
    }
    ]
  },
  options: {
    responsive:RESPONSIVE_BOOL,
    scales: {
      xAxes: [{
        ticks: {
          display:XAXES_DISPLAY_BOOL //this will remove only the label
        }
      }]
    }
  }
});

