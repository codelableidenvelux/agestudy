// This script makes a horizontal barchart that shows the money earned so far
// For each participant, it gets the money earned so far from the home template
// when rendered
// on ready get the price chose the max value on the price log
// Source: https://bl.ocks.org/hrecht/f84012ee860cb4da66331f18d588eee3
$(document).ready(function() {
if (document.getElementById("barChart")){
  var price = d3.select("#price").attr("value")
  if (price < 10){
    maxVal = 26
  }
  else if(price > 10 && price < 30){
    maxVal = 50
  }
  else{
    maxVal = 200
  }
  // set the data in the right format
  var data = [
    {"name": "€",
    "value": maxVal,
    // opacity is 0 as not to show this rect
    "opacity": "0",
    // just attach a random color it will not show since opacity is 0
    "color": "white"},
    { "name": "€",
    "value": price,
    // opacity is 1 to show this rect
    "opacity": "1",
    // this is the color of the rect
    "color": "#ff7632"}
  ]
  // make the barchart by calling the barchart function

  barChart(data)
}
});

function barChart(data){
  //set up svg using margin conventions - we'll need plenty of room on the left for labels
  var margin = {
    top: 40,
    right: 50,
    bottom: 30,
    left: 30
  };

  // set the width and height
  var width = 600 - margin.left - margin.right,
  height = 100 - margin.top - margin.bottom;

  // append an svg with a g tag
  var svg = d3.select("#barChart").append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");



  // x scale
  var x = d3.scaleLinear()
  .rangeRound([0, width])
  .domain([0, d3.max(data, function (d) {
    return d.value;
  })]);

  // y scale
  var y = d3.scaleBand()
  .rangeRound([height, 0])
  .domain(data.map(function (d) {
    return d.name;
  }));

  //make y axis to show bar names
  var yAxis = d3.axisLeft(y)
  //no tick marks
  .tickSize(0);
  //make x axis to price range
  var xAxis = d3.axisBottom(x)
  .tickSize(1);

  // append the y axis to the svg
  var gy = svg.append("g")
  .attr("class", "y axis")
  .call(yAxis)

  // append the x axis to the svg
  var gx = svg.append("g")
  .attr("class", "x axis")
  .attr("transform", "translate(0," + height + ")")
  .style("font-size", 14)
  .call(xAxis)
  //attach as many bars as there are data
  var bars = svg.selectAll(".bar")
  .data(data)
  .enter()
  .append("g")

  //append rects
  bars.append("rect")
  .attr("class", "bar")
  .attr("y", function (d) {
    return y(d.name);
  })
  .attr("height", y.bandwidth())
  .attr("x", 0)
  .attr("width", function (d) {
    return x(d.value);
  })
  .attr("fill",function(d){ return d.color })
  .style("opacity", function(d){ return d.opacity });

  //add a value label to the right of each bar
  bars.append("text")
  .attr("class", "label")
  //y position of the label is halfway down the bar
  .attr("y", function (d) {
    return y(d.name) + y.bandwidth() / 2 + 4;
  })
  //x position is 3 pixels to the right of the bar
  .attr("x", function (d) {
    return x(d.value) + 3;
  })
  .text(function (d) {
    return d.value + "€";
  })
  .style("opacity", function(d){ return d.opacity });
};
