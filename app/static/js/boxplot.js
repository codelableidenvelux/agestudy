function boxplot(response){
  $.getScript("../static/js/d3-tip.js")
  .fail(function( jqxhr, settings, exception ) {
    console.log("fail")
  });
  data = response[0]["basic_stats"]["quantiles_summary"]
  var average_year = new Date(response[0]["basic_stats"]["average_year"]);
  var today = new Date();
  var average_age = today.getFullYear() - average_year.getFullYear()
  // add a title
  d3.select(".average_age")
  .text("Average age: " + average_age);
  // set the dimensions and margins of the graph
  var margin = {top: 80, right: 50, bottom: 30, left: 40},
  width = 200 - margin.left - margin.right,
  height = 400 - margin.top - margin.bottom;

  // append the svg object to the body of the page
  var svg = d3.select(".boxplot")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform",
  "translate(" + margin.right + "," + margin.top + ")");

  var q1 = data["q1"]
  var median = data["median"]
  var q3 = data["q3"]
  var interQuantileRange = q3 - q1
  var min = data["lower_bound"]
  var max = data["max"]

  // Show the Y scale
  var y = d3.scaleLinear()
  .domain([data["min"],max])
  .range([height, 0])


  svg.call(d3.axisLeft(y).ticks(10, "d"))

  // a few features for the box
  var center = 100
  var width = 100

  var tool_tip = d3.tip()
  .attr("class", "d3-tip")
  .offset([15, 25])
  .html(function(d) { return d; });
  svg.call(tool_tip);
  // add a title
  svg.append("text")
  .attr("x", ((width + margin.right) / 2))
  .attr("y", 0 - (margin.top / 2))
  .attr("text-anchor", "middle")
  .style("font-size", "18px")
  .attr("fill", "black")
  .text("Age distrubution");

  // text label for the y axis
 svg.append("text")
     .attr("transform", "rotate(-90)")
     .attr("y", 0 - margin.right)
     .attr("x",0 - (height / 2))
     .attr("dy", "1em")
     .style("text-anchor", "middle")
     .attr("fill", "black")
     .text("Year");

  // Show the main vertical line
  svg
  .append("line")
  .attr("x1", center)
  .attr("x2", center)
  .attr("y1", y(min) )
  .attr("y2", y(max) )
  .attr("stroke", "black")
  .style("stroke-width", 3)
  .style("stroke-dasharray", "0.5em");

  // Show the box
  svg
  .append("rect")
  .attr("x", center - width/2)
  .attr("y", y(q3) )
  .attr("height", (y(q1)-y(q3)) )
  .attr("width", width )
  .attr("stroke", "black")
  .style("fill", "#69b3a2")

  svg.selectAll(".dot")
  .data(data["outliers"])
  .enter().append("circle")
  .attr("class", "dot")
  .attr("r", 3.5)
  .attr("cx", center)
  .attr("cy", function (d) { return y(d); })
  .attr("fill", "#ffffff")
  .style("stroke", function(d) { return "black";})
  .on('mouseover', function(d) {
    tool_tip.show(d);
  })
  .on('mouseout', function(d){
    tool_tip.hide();
  });

  // show median, min and max horizontal lines
  svg
  .selectAll("toto")
  .data([min, median, max, q1, q3])
  .enter()
  .append("line")
  .attr("x1", center-width/2)
  .attr("x2", center+width/2)
  .attr("y1", function(d){ return(y(d))} )
  .attr("y2", function(d){ return(y(d))} )
  .attr("stroke", "black")
  .style("stroke-width", 3)
  .on('mouseover', function(d) {
    tool_tip.offset([15,90])
    tool_tip.show(d);
  })
  .on('mouseout', function(d){
    tool_tip.offset([15,25])
    tool_tip.hide();
  });

}
