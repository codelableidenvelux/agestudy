function gender_barchart(response){
  var data = response[0]["basic_stats"]["gender"]
  console.log(data)
  var gender_mode_num = response[0]["basic_stats"]["gender_mode"]
  var gender_mode = ""
  if (gender_mode_num == 1){
    gender_mode = "male"
  }
  else if (gender_mode_num == 2){
    gender_mode = "female"
  }
  else{
    gender_mode = "other"
  }
  d3.select(".gender_mode")
  .text("Gender mode: " + gender_mode);
  return data
}

function user_type_barchart(response){
  var data = response[0]["basic_stats"]["user_type"]
  console.log(data)
  var user_type_mode_num = response[0]["basic_stats"]["user_type_mode"]
  var user_type_mode = ""
  if (user_type_mode_num == 1){
    user_type_mode = "paid"
  }
  else{
    user_type_mode = "unpaid"
  }
  d3.select(".user_type_mode")
  .text("User Type mode: " + user_type_mode);
  return data
}

function barchart(data, div_class, selects){

  // set the dimensions and margins of the graph
var margin = {top: 80, right: 50, bottom: 30, left: 40},
    width = 200 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;


// set the ranges
var x = d3.scaleBand()
          .range([0, width])
          .padding(0.1);
var y = d3.scaleLinear()
          .range([height, 0]);

// append the svg object to the body of the page
// append a 'group' element to 'svg'
// moves the 'group' element to the top left margin
var svg = d3.select(div_class).append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

          // text label for the y axis
         svg.append("text")
             .attr("transform", "rotate(-90)")
             .attr("y", 0 - margin.left)
             .attr("x",0 - (height / 2))
             .attr("dy", "1em")
             .style("text-anchor", "middle")
             .attr("fill", "black")
             .style("font-size", 10)
             .text("Frequency");

  var color = d3.scaleOrdinal(d3.schemeSet2);

  var tool_tip = d3.tip()
  .attr("class", "d3-tip")
  .offset([0, 0])
  .html(function(d) { return d[selects[0]] + ": " + d[selects[1]]; });
  svg.call(tool_tip);
  // Scale the range of the data in the domains
  x.domain(data.map(function(d) { return d[selects[0]]; }));
  y.domain([0, d3.max(data, function(d) { return d[selects[1]]; })]);

  // append the rectangles for the bar chart
  svg.selectAll(".bar")
      .data(data)
    .enter().append("rect")
      .attr("class", "bar")
      .attr("x", function(d) { return x(d[selects[0]]); })
      .attr("fill", function(d) { return color(d[selects[0]])})
      .attr("width", x.bandwidth())
      .attr("y", function(d) { return y(d[selects[1]]); })
      .attr("height", function(d) { return height - y(d[selects[1]]); })
      .on('mouseover', function(d) {
        tool_tip.show(d);
      })
      .on('mouseout', function(d){
        tool_tip.hide();
      });

  // add the x Axis
  svg.append("g")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));

  // add the y Axis
  svg.append("g")
      .call(d3.axisLeft(y).ticks(5));


}
