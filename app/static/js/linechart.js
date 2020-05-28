// https://bl.ocks.org/LemoNode/a9dc1a454fdc80ff2a738a9990935e9d
// tooltip
// https://jsfiddle.net/8reo2Lvc/
function linechart(response){
  str_data = response[0]["streamgraph_data"]
  data = JSON.parse(str_data)
  console.log(data)
  for (i in data){
    data[i]["time_exec_ymd"] = new Date(data[i]["time_exec_ymd"])
  }
    data.sort(function(a, b) { return (a.time_exec_ymd - b.time_exec_ymd )} )

  var keys = ["corsi","n_back", "t_switch", "sf_36", "phone", "rt"]

  var svg = d3.select(".linechart").append('svg').attr("height", 500).attr("width", 1500)
  var margin = {top: 15, right: 35, bottom: 15, left: 80},
  width = 1000 - margin.left - margin.right,
  height = 500 - margin.top - margin.bottom;


  var  x = d3.scaleUtc()
  .domain(d3.extent(data, d => d.time_exec_ymd))
  .rangeRound([margin.left, width - margin.right])

  var y = d3.scaleLinear()
  .rangeRound([height - margin.bottom, margin.top]);

  var color = d3.scaleOrdinal(d3.schemeSet2);

  var line = d3.line()
  .x(function(d) { return x(d.date)})
  .y(d => y(d.degrees));

  svg.append("g")
  .attr("class","x-axis")
  .attr("transform", "translate(0," + (height - margin.bottom) + ")")
  .call(d3.axisBottom(x).tickFormat(d3.timeFormat("%b %d")));

  svg.append("g")
  .attr("class", "y-axis")
  .attr("transform", "translate(" + margin.left + ",0)");



     // text label for the y axis
    svg.append("text")
        .attr("y", height + (margin.bottom/2))
        .attr("x", width / 2)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .attr("fill", "black")
        .style("font-size", 10)
        .text("Time executed");

  var focus = svg.append("g")
  .attr("class", "focus")
  .style("display", "none");

  focus.append("line").attr("class", "lineHover")
  .style("stroke", "#999")
  .attr("stroke-width", 3)
  .style("shape-rendering", "crispEdges")
  .style("opacity", 0.5)
  .attr("y1", -height)
  .attr("y2",0);

  focus.append("text").attr("class", "lineHoverDate")
  .attr("text-anchor", "middle")
  .attr("font-size", 12);

  focus.append("rect")
        .attr("class", "text_background")
        .attr("opacity", 0.3)
        .attr("x", 9)
        .attr("dy", ".35em")
        .attr("width", 120)
        .attr("height", 175)

  var overlay = svg.append("rect")
  .attr("class", "overlay")
  .attr("x", margin.left)
  .attr("width", width - margin.right - margin.left)
  .attr("height", height)

  update(d3.select('#selectbox').property('value'), 0);

  function update(input, speed) {
    var copy = keys

    var cities = copy.map(function(id) {
      return {
        id: id,
        values: data.map(d => {return {date: d.time_exec_ymd, degrees: +d[id]}})
      };
    });

    console.log(cities)

    y.domain([
      d3.min(cities, d => d3.min(d.values, c => c.degrees)),
      d3.max(cities, d => d3.max(d.values, c => c.degrees))
    ]);

    svg.selectAll(".y-axis")
    .transition()
    .duration(speed)
    .call(d3.axisLeft(y).tickSize(-width + margin.right + margin.left))

    var city = svg.selectAll(".cities")
    .data(cities);


    city.exit().remove();

    city.enter().insert("g", ".focus").append("path")
    .attr("class", "line cities")
    .style("stroke", function(d){ return color(d.id)})
    .merge(city)
    .transition()
    .duration(speed)
    .attr("d", function(d) { return line(d.values)})

    tooltip(copy);
  }

  function tooltip(copy) {

    var labels = focus.selectAll(".lineHoverText")
    .data(copy)

    labels.enter().append("text")
    .attr("class", "lineHoverText")
    .style("fill", d => color(d))
    .attr("text-anchor", "start")
    .attr("font-size",12)
    .attr("dy", (_, i) => 1 + i * 2 + "em")
    .merge(labels);

    var circles = focus.selectAll(".hoverCircle")
    .data(copy)

    circles.enter().append("circle")
    .attr("class", "hoverCircle")
    .style("fill", d => color(d))
    .attr("r", 4.5)
    .merge(circles);

    svg.selectAll(".overlay")
    .on("mouseover", function() { focus.style("display", null); })
    .on("mouseout", function() { focus.style("display", "none"); })
    .on("mousemove", mousemove);

    var bisectDate = d3.bisector(d => d.time_exec_ymd).left
    var formatDate = d3.timeFormat("%Y-%m-%d")
    formatValue = d3.format(",.0f");

    function mousemove() {

      var x0 = x.invert(d3.mouse(this)[0])
      var	i = bisectDate(data, x0, 1)
      var	d0 = data[i - 1]
      var	d1 = data[i]
      var	d = x0 - d0.time_exec_ymd > d1.time_exec_ymd - x0 ? d1 : d0;

      focus.select(".lineHover")
      .attr("transform", "translate(" + x(d.time_exec_ymd) + "," + height + ")");

      focus.select(".lineHoverDate")
      .attr("transform",
      "translate(" + x(d.time_exec_ymd) + "," + (height + margin.bottom) + ")")
      .text(formatDate(d.time_exec_ymd));

      focus.selectAll(".hoverCircle")
      .attr("cy", e => y(d[e]))
      .attr("cx", x(d.time_exec_ymd));

      focus.select(".text_background")
            .attr("transform",
                  "translate(" + (x(d.time_exec_ymd)) + "," + height / 2.5 + ")")

      focus.selectAll(".lineHoverText")
      .attr("transform",
      "translate(" + (x(d.time_exec_ymd)) + "," + height / 2.5 + ")")
      .text(e => e + " " + formatValue(d[e]))
      .style("font-weight", "bold")
      .style("font-size", 15);

      x(d.time_exec_ymd) > (width - width / 4)
      ? focus.selectAll("text.lineHoverText")
      .attr("text-anchor", "end")
      .attr("dx", -10)
      : focus.selectAll("text.lineHoverText")
      .attr("text-anchor", "start")
      .attr("dx", 10)

      x(d.time_exec_ymd) > (width - width / 4)
      ? focus.select(".text_background")
      .attr("transform",
            "translate("  + (x(d.time_exec_ymd)  - 135)  + "," + height / 2.5 + ")")
      : focus.select(".text_background")
             .attr("dx", 10)
    }
  }

  var selectbox = d3.select("#selectbox")
  .on("change", function() {
    update(this.value, 750);
  })

  legend(keys, color, ".legend", 150, 150)
}
