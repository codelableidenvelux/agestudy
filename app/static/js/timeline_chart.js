function timeline_chart(timeline_data){
  console.log(timeline_data)
  milestones('.timeline_chart')
    .mapping({
      'timestamp': 'date',
      'text': 'type'
    })
    .aggregateBy('day')
    .labelFormat('%d-%m')
    .render(timeline_data);
}



function timeline_chart_2(timeline_data){
  data = timeline_data
  keys = ["sign_up","corsi", "n_back", "task_switching", "sf-36", "phone_survey", "rt"]
  var color = d3.scaleOrdinal()
                .range(["#8dd3c7","#ffffb3","#bebada","#fb8072","#80b1d3","#fdb462","#b3de69"])
                .domain(keys)


  var formatDateIntoYear = d3.timeFormat("%d-%m");
var formatDate = d3.timeFormat("%b %Y");
var parseDate = d3.timeParse("%m/%d/%y");


sign_up_date = new Date(data[0].date.valueOf())
var startDate = sign_up_date.setDate(sign_up_date.getDate() - 5),
  endDate = new Date();

function get_width(div){
  var bb = document.querySelector(div)
                      .getBoundingClientRect(),
         width_div = bb.right - bb.left;
         return width_div
}

var margin = {top:50, right:50, bottom:0, left:50},
  width = get_width('.timeline_chart') - margin.left - margin.right,
  height = 300 - margin.top - margin.bottom;

var svg = d3.select(".timeline_chart")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom);

////////// slider //////////

var moving = false;
var currentValue = 0;
var targetValue = width;

var playButton = d3.select("#play-button");

var x = d3.scaleTime()
  .domain([startDate, endDate])
  .range([0, width])
  .clamp(true)
  .nice();

var slider = svg.append("g")
  .attr("class", "slider")
  .attr("transform", "translate(" + margin.left + "," + height/5 + ")");

slider.append("line")
  .attr("class", "track")
  .attr("x1", x.range()[0])
  .attr("x2", x.range()[1])
.select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
  .attr("class", "track-inset")
.select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
  .attr("class", "track-overlay")
  .call(d3.drag()
      .on("start.interrupt", function() { slider.interrupt(); })
      .on("start drag", function() {
        currentValue = d3.event.x;
        update(x.invert(currentValue));
      })
  );

slider.insert("g", ".track-overlay")
  .attr("class", "ticks")
  .attr("transform", "translate(0," + 18 + ")")
.selectAll("text")
  .data(x.ticks(10))
  .enter()
  .append("text")
  .attr("x", x)
  .attr("y", 10)
  .attr("text-anchor", "middle")
  .text(function(d) { return formatDateIntoYear(d); });

var handle = slider.insert("circle", ".track-overlay")
  .attr("class", "handle")
  .attr("r", 9);

var label = slider.append("text")
  .attr("class", "label")
  .attr("text-anchor", "middle")
  .text(formatDate(startDate))
  .attr("transform", "translate(0," + (-25) + ")")


////////// plot //////////

var plot = svg.append("g")
  .attr("class", "plot")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

drawPlot(data, color);

playButton
  .on("click", function() {
  var button = d3.select(this);
  if (button.text() == "Pause") {
    moving = false;
    clearInterval(timer);
    // timer = 0;
    button.text("Play");
  } else {
    moving = true;
    timer = setInterval(step, 100);
    button.text("Pause");
  }
  console.log("Slider moving: " + moving);
})

function prepare(d) {
d.id = d.id;
d.date = parseDate(d.date);
return d;
}

function step() {
update(x.invert(currentValue));
currentValue = currentValue + (targetValue/151);
if (currentValue > targetValue) {
  moving = false;
  currentValue = 0;
  clearInterval(timer);
  // timer = 0;
  playButton.text("Play");
  console.log("Slider moving: " + moving);
}
}


function drawPlot(data,color) {
var locations = plot.selectAll(".location")
  .data(data);
  console.log(data)

// if filtered dataset has more circles than already existing, transition new ones in
locations.enter()
  .append("circle")
  .attr("class", "location")
  .attr("cx", function(d) { return x(d.date); })
  .attr("cy", height/2)
  .style("fill", function(d) { return color(d.type)})
  .style("stroke", function(d) { console.log(d.type)
    return color(d.type)})
  .style("stroke-width", 2)
  .style("fill-opacity", 1)
  .attr("r", 20)
    .transition()
    .duration(100)
    .attr("r", 40)
      .transition()
      .attr("r", 20);

// if filtered dataset has less circles than already existing, remove excess
locations.exit()
  .remove();
}

function update(h) {
// update position and text of label according to slider scale
handle.attr("cx", x(h));
label
  .attr("x", x(h))
  .text(h);

// filter data set and redraw plot
var newData = data.filter(function(d) {
  return d.date < h;
})
drawPlot(newData, color);
}
legend(keys, color, ".legend_timeline_chart", get_width('.legend_timeline_chart'), 200)
}
