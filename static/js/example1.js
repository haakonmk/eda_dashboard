//const CSV =
//    "https://raw.githubusercontent.com/chris3edwards3/exampledata/master/plotlyJS/line.csv";
const CSV =
  "input_files/RR1_CSV.csv";

var json = fetch("RR1_CSV0.json")
  .then(res => res.json())
  .then(data => console.log(data))

for (var key in json) {
if (json.hasOwnProperty(key)) {
  alert(json[key].id);
  alert(json[key].msg);
}
}

function plotFromCSV() {
  Plotly.d3.csv(CSV, function(err, rows) {
    console.log(rows);
    processData(rows);
  });
}

function processData(allRows) {
  let x = [];
  let y1 = [];
  let y2 = [];
  let y3 = [];
  let y4 = [];
  let y5 = [];
  let row;

  let i = 0;
  while (i < allRows.length) {
    row = allRows[i];
    x.push(row["Controller_Time_GMT"]);
    y1.push(row["Temp_degC_Ground"]);
    y2.push(row["Temp_degC_ISS"]);
    y3.push(row["RH_percent_Ground"]);
    y4.push(row["RH_percent_ISS"]);
    y5.push(row["CO2_ppm_ISS"]);
    i += 1;
  }

  console.log("X", x);
  console.log("Y1", y1);

  makePlotly1(x, y1, y2);
  makePlotly2(x, y3, y4);
  makePlotly3(x,y5);
}

function makePlotly1(x, y1, y2) {
  let traces = [{
      x: x,
      y: y1,
      name: "A",
      line: {
        color: "#387fba",
        width: 3
      }
    },
    {
      x: x,
      y: y2,
      name: "B",
      line: {
        color: "#54ba38",
        width: 3,
        // dash: "dash"
      }
    }
  ];

  let layout = {
    title: "Temperature",
    yaxis: {
      range: [15, 30]
    },
    xaxis: {
      // tickformat: "%d/%m/%y"
    },
  };

  //https://plot.ly/javascript/configuration-options/
  let config = {
    responsive: true,
    // staticPlot: true,
    // editable: true
  };

  Plotly.newPlot("plot", traces, layout, config);
}

function makePlotly3(x, y5) {
  let traces = [{
      x: x,
      y: y5,
      name: "C"
    }
  ];

  let config = {
    responsive: true,
    // staticPlot: true,
    // editable: true
  };

  Plotly.newPlot("plot3", traces, config);
}



function makePlotly2(x, y3, y4) {

  var frames = [{
      name: 'C02ISS',
      data: [{
        x: x,
        y: y3
      }]
    },
    {
      name: 'CO2GROUND',
      data: [{
        x: x,
        y: y4
      }]
    },
  ];
  let traces = [{
    x: frames[0].data[0].x,
    y: frames[0].data[0].y,
    }
  ];
  let layout = {
    title: "CO2",
    xaxis: {
      tickformat: "%d/%m/%y"
    },
  };

  //https://plot.ly/javascript/configuration-options/
  let config = {
    title: "CO2",
    responsive: true,
    xaxis: {
      tickformat: "%d/%m/%y"
    },
    updatemenus: [{
      buttons: [{
          method: 'animate',
          args: [
            ['C02ISS']
          ],
          label: 'C02ISS'
        },
        {
          method: 'animate',
          args: [
            ['CO2GROUND']
          ],
          label: 'CO2GROUND'
        },
      ],
      title: "CO2",
      xaxis: {
        tickformat: "%d/%m/%y"
      },
    }],
  };


  Plotly.newPlot('plot2', traces, config).then(function() {
    Plotly.addFrames('plot2', frames);
  });
}






plotFromCSV();
