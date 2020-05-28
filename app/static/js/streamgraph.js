// https://www.d3-graph-gallery.com/graph/streamgraph_template.html
// https://observablehq.com/@d3/streamgraph

// tooltip
// https://jsfiddle.net/8reo2Lvc/
function streamgraph(response){
  console.log(response)
  str_data = response[0]["streamgraph_data"]
  data = JSON.parse(str_data)
  console.log(data)
  for (i in data){
    data[i]["time_exec_ymd"] = new Date(data[i]["time_exec_ymd"])
  }
  data.sort(function(a, b) { return (a.time_exec_ymd - b.time_exec_ymd )} )
  // color palette
  var color = d3.scaleOrdinal(d3.schemeSet2)
  // set the dimensions and margins of the graph
  var margin = {top: 70, right: 30, bottom: 30, left: 60},
  width = 1000 - margin.left - margin.right,
  height = 500 - margin.top - margin.bottom;

  // append the svg object to the body of the page
  var svg = d3.select(".streamgraph")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform",
  "translate(" + margin.left + "," + margin.top + ")");
  // List of groups = header of the csv files
  var keys = ["corsi","n_back", "t_switch", "sf_36", "phone_survey", "rt"]


  x = d3.scaleUtc()
    .domain(d3.extent(data, d => d.time_exec_ymd))
    .range([0, width])


  svg.append("g")
  .attr("transform", "translate(0," + height + ")")
  .call(d3.axisBottom(x).ticks(10));

  stacked_data = d3.stack().keys(keys)(data)
  series = d3.stack()
    .keys(keys)
    .offset(d3.stackOffsetWiggle)
    .order(d3.stackOrderInsideOut)
  (data)


  // Add Y axis
  var y = d3.scaleLinear()
  .domain([0, Math.ceil(d3.max(series, d => d3.max(d, d => d[1])) + 1)])
  .range([ height, 0 ]);

  svg.append("g")
  .call(d3.axisLeft(y).ticks(10));



  // create a tooltip
var Tooltip = svg
  .append("text")
  .attr("x", width/2)
  .attr("y", 0)
  .style("opacity", 0)
  .style("font-size", 30)

// Three function that change the tooltip when user hover / move / leave a cell
var mouseover = function(d) {
  Tooltip.style("opacity", 1)
  d3.selectAll(".myArea").style("opacity", .2)
  d3.select(this)
    .style("stroke", "black")
    .style("opacity", 1)
}
var mousemove = function(d,i) {
  grp = keys[i]
  Tooltip.text(grp)
}
var mouseleave = function(d) {
  Tooltip.style("opacity", 0)
  d3.selectAll(".myArea").style("opacity", 1).style("stroke", "none")
 }



  // Show the areas
  svg
  .selectAll("mylayers")
  .data(d3.stack().keys(keys)(data))
  .enter()
  .append("path")
  .attr("class", "myArea")
  .style("fill", function(d) { return color(d.key); })
  .attr("d",
    d3.area()
      .x(function(d, i) { return x(d.data.time_exec_ymd); })
     .y0(function(d) {  return y(d[0]); })
    .y1(function(d) {  return y(d[1]); })
    )
    .on("mouseover", mouseover)
      .on("mousemove", mousemove)
      .on("mouseleave", mouseleave)

      // text label for the y axis
     svg.append("text")
         .attr("transform", "rotate(-90)")
         .attr("y", 0 - margin.left)
         .attr("x",0 - (height / 2))
         .attr("dy", "1em")
         .style("text-anchor", "middle")
         .attr("fill", "black")
         .style("font-size", 10)
         .text("Tasks completion ratio");

         // text label for the y axis
        svg.append("text")
            .attr("y", height + (margin.bottom/2))
            .attr("x", width / 2)
            .attr("dy", "1em")
            .style("text-anchor", "middle")
            .attr("fill", "black")
            .style("font-size", 10)
            .text("Time executed");

  legend(keys, color, ".legend", 150, 150)
}
