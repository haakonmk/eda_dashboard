function create_plot(dataJSON){
  var trace1 = {
    x: dataJSON.x1,
    y: dataJSON.y1,
    mode: 'lines',
    type: 'scatter',
    name: "A",
    line: {
      color: "#387fba",
      width: 2
    }
  };

  var trace2 = {
    x: dataJSON.x2,
    y: dataJSON.y2,
    mode: 'lines',
    type: 'scatter'
  };


  var data = [trace1, trace2];

  var layout = {
     xaxis: {
       title: {
         text: 'X',
       },
     },
     yaxis: {
       title: {
         text: 'Y',
       }
     },
     showlegend: true,
   };


   Plotly.newPlot('plot', data, layout);
}


function create_plot2(dataJSON){
  var trace1 = {
    x: dataJSON.x1,
    y: dataJSON.y1,
    mode: 'lines',
    type: 'scatter'
  };

  var trace2 = {
    x: dataJSON.x2,
    y: dataJSON.y2,
    mode: 'lines',
    type: 'scatter'
  };


  var data = [trace1, trace2];

  var layout = {
     xaxis: {
       title: {
         text: 'X',
       },
     },
     yaxis: {
       title: {
         text: 'Y',
       }
     },
     showlegend: true,
   };


   Plotly.newPlot('plot2', data, layout);
}


function create_plot3(dataJSON){
  var trace1 = {
    x: dataJSON.x_timestamp,
    y: dataJSON.Temp_degC_Ground,
    mode: 'lines',
    name: 'Temp_degC_Ground',
    type: 'scatter'
  };

  var trace2 = {
    x: dataJSON.x_timestamp,
    y: dataJSON.Temp_degC_ISS,
    name: 'Temp_degC_ISS',
    mode: 'lines',
    type: 'scatter'
  };


  var data = [trace1, trace2];

  var layout = {
     xaxis: {
       title: {
         text: 'X',
       },
     },
     yaxis: {
       title: {
         text: 'Y',
       }
     },
     showlegend: true,
   };


   Plotly.newPlot('plot3', data, layout);
}
