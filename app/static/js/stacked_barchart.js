//
function stacked_barchart(response){
  $.getScript("../static/js/d3-tip.js")
  .fail(function( jqxhr, settings, exception ) {
    console.log("fail")
  });
  // create the svg
  data = response[0]["tasks"]

  var svg = d3.select(".stacked_barchart").append("svg").attr("height", 500).attr("width", 1000)

  var margin = {top: 20, right: 20, bottom: 50, left: 70}
  var width = 500 - margin.left - margin.right
  var height = 500 - margin.top - margin.bottom
  var g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // set x scale
  var x = d3.scaleBand()
  .rangeRound([0, width])
  .paddingInner(0.05)
  .align(0.1);

  // set y scale
  var y = d3.scaleLinear()
  .rangeRound([height, 0]);

  // set the colors
  var z = d3.scaleOrdinal(d3.schemeSet2)

  for (i in data){
    data[i]["total"] = data[i].complete + data[i].incomplete
  }

  data.sort(function(a, b) { return b.total - a.total; });
  keys = ["complete", "incomplete"]
  x.domain(data.map(function(d) { return d.task; }));
  y.domain([0, d3.max(data, function(d) { return d.total; })]).nice();
  z.domain(keys);


  g.append("g")
  .selectAll("g")
  .data(d3.stack().keys(keys)(data))
  .enter().append("g")
  .attr("class", "data")
  .attr("fill", function(d) { return z(d.key); })
  .selectAll("rect")
  .data(function(d) { return d; })
  .enter().append("rect")
  .attr("x", function(d) { return x(d.data.task); })
  .attr("y", function(d) { return y(d[1]); })
  .attr("height", function(d) { return y(d[0]) - y(d[1]); })
  .attr("width", x.bandwidth())
  .on('mouseover', function(d) {
    tool_tip.show(d);
  })
  .on('mouseout', function(d){
    tool_tip.hide();
  });

  var tool_tip = d3.tip()
  .attr("class", "d3-tip")
  .offset([-8, 0])
  .html(function(d) { return "Tasks: " + (d[1] - d[0]); });
  svg.call(tool_tip);

  g.append("g")
  .attr("class", "axis")
  .attr("transform", "translate(0," + height + ")")
  .call(d3.axisBottom(x));

  g.append("g")
  .attr("class", "axis")
  .call(d3.axisLeft(y).ticks(null, "s"))
  .append("text")
  .attr("x", 2)
  .attr("y", y(y.ticks().pop()) + 0.5)
  .attr("dy", "0.32em")
  .attr("fill", "#000")
  .attr("font-weight", "bold")
  .attr("text-anchor", "start");

  var legend = g.append("g")
  .attr("font-family", "sans-serif")
  .attr("font-size", 10)
  .attr("text-anchor", "end")
  .selectAll("g")
  .data(keys.slice().reverse())
  .enter().append("g")
  .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

  legend.append("rect")
  .attr("x", width - 19)
  .attr("width", 19)
  .attr("height", 19)
  .attr("fill", z);

  legend.append("text")
  .attr("x", width - 24)
  .attr("y", 9.5)
  .attr("dy", "0.32em")
  .text(function(d) { return d; });

  // text label for the y axis
 svg.append("text")
     .attr("transform", "rotate(-90)")
     .attr("y", margin.left/2)
     .attr("x",0 - (height / 2))
     .attr("dy", "1em")
     .style("text-anchor", "middle")
     .attr("fill", "black")
     .style("font-size", 10)
     .text("Num tasks execution");

     // text label for the y axis
    svg.append("text")
        .attr("y", height + (margin.bottom))
        .attr("x", width / 2)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .attr("fill", "black")
        .style("font-size", 10)
        .text("Tasks");

}
