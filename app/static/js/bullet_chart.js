function bullet_chart(response){
  $.getScript("../static/js/bullet.js")
  .fail(function( jqxhr, settings, exception ) {
    console.log("fail")
  });
  console.log(response)
var data =  response[0]["bullet"]


var margin = {top: 50, right: 40, bottom: 20, left: 150},
    width = 800 - margin.left - margin.right,
    height = 100 - margin.top - margin.bottom;

var chart = d3.bullet()
    .width(width)
    .height(height);

    var svg = d3.select(".bullet_chart").selectAll("svg")
         .data(data)
       .enter().append("svg")
      .attr("class", "bullet")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
      .call(chart)
      .on('mouseover', function(d) {
        tool_tip.show(d);
      })
      .on('mouseout', function(d){
        tool_tip.hide();
      });

      var tool_tip = d3.tip()
      .attr("class", "d3-tip")
      .direction('n')
      .html(function(d) { return "Reaction time: " + d["ranges"][0] + " -- Survey: "
      + d["ranges"][1] + "<br/> Tasks: " +  d["measures"] + " -- Total: " + d["ranges"][2]; })
      .attr("data-html", "true");
      svg.call(tool_tip);


  var title = svg.append("g")
      .style("text-anchor", "end")
      .attr("transform", "translate(-6," + height / 2 + ")");

  title.append("text")
      .attr("class", "title")
      .text(function(d) { return d.title; });

  title.append("text")
      .attr("class", "subtitle")
      .attr("dy", "1em")
      .text(function(d) { return d.subtitle; });

  var color = d3.scaleOrdinal()
                 .range(["#98AFC7", "#fc8d62","#4682B4", "#ccc"]);

keys = ["rt", "survey", "tasks", "total"]
legend(keys, color, ".legend_bullet_chart", 150, 150)
}
