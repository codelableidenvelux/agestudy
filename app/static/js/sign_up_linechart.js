function sign_up_linechart(response){
  var str_data = response[0]["sign_up"];
  var data = JSON.parse(str_data);
  for (i in data){
    data[i]["time_sign_up_ymd"] = new Date(data[i]["time_sign_up_ymd"]);
  }
  data.sort(function(a, b) { return (a.time_sign_up_ymd - b.time_sign_up_ymd )} )

  // set the dimensions and margins of the graph
var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 500 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

// parse the date / time
var parseTime = d3.timeFormat("%d-%b-%y");

// set the ranges
var x = d3.scaleUtc().range([0, width]);
var y = d3.scaleLinear().range([height, 0]);

// define the line
var valueline = d3.line()
    .x(function(d) { return x(d.time_sign_up_ymd); })
    .y(function(d) { return y(d.email); });

// append the svg obgect to the body of the page
// appends a 'group' element to 'svg'
// moves the 'group' element to the top left margin
var svg = d3.select(".sign_up_linechart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");


  // Scale the range of the data
  x.domain(d3.extent(data, function(d) { return d.time_sign_up_ymd; }));
  y.domain([0, d3.max(data, function(d) { return d.email; })]);
  var tool_tip = d3.tip()
  .attr("class", "d3-tip")
  .offset([0, 0])
  .html(function(d) { return "Date: " + parseTime(d.time_sign_up_ymd) + " -- Value: " + d.email; });
  svg.call(tool_tip);
  // Add the valueline path.
  svg.append("path")
      .attr("class", "line")
      .attr("d", valueline(data));

      // 12. Appends a circle for each datapoint
    svg.selectAll(".dot")
        .data(data)
      .enter().append("circle") // Uses the enter().append() method
        .attr("class", "dot") // Assign a class for styling
        .attr("cx", function(d, i) { return x(d.time_sign_up_ymd) })
        .attr("cy", function(d) { return y(d.email) })
        .attr("r", 5)
        .attr("fill", "#66c2a5")
        .on('mouseover', function(d) {
          tool_tip.show(d);
        })
        .on('mouseout', function(d){
          tool_tip.hide();
        });
        // text label for the y axis
       svg.append("text")
           .attr("transform", "rotate(-90)")
           .attr("y", 0 - margin.left)
           .attr("x",0 - (height / 2))
           .attr("dy", "1em")
           .style("text-anchor", "middle")
           .attr("fill", "black")
           .style("font-size", 10)
           .text("Number of sign ups");

           // text label for the y axis
          svg.append("text")
              .attr("y", height + (margin.bottom/2))
              .attr("x", width / 2)
              .attr("dy", "1em")
              .style("text-anchor", "middle")
              .attr("fill", "black")
              .style("font-size", 10)
              .text("Sign up time");
  // Add the X Axis
  svg.append("g")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x).ticks(5).tickFormat(d3.timeFormat("%b %Y")));

  // Add the Y Axis
  svg.append("g")
      .call(d3.axisLeft(y));
}
