function create_plot(dataJSON){
  var trace1 = {
    x: dataJSON.x1,
    y: dataJSON.y1,
    mode: 'markers',
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


   Plotly.newPlot('plot', data, layout);
}
