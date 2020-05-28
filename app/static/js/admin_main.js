window.onload = function()
{
  var requests = [d3.json("/get_data")]
  Promise.all(requests).then(function(response) {
    stacked_barchart(response)
    streamgraph(response)
    boxplot(response)
    var data_gender = gender_barchart(response)
    barchart(data_gender, ".gender_barchart", ["gender", "value"])
    var data_user_type = user_type_barchart(response)
    barchart(data_user_type, ".user_type_barchart", ["user_type", "value"])
    basic_info(response)
    bullet_chart(response)
    sign_up_linechart(response)
  }).catch(function(e) {
      throw(e);
  });
};
function basic_info(response){
  var data = response[0]["basic_stats"]
  d3.select(".num_p")
    .text("Number of participants: " + data["num_p"]);

    d3.select(".num_active_p")
      .text("Number of active participants: " + data["num_active_p"]);
}

function toggle_charts(chart){
  var requests = [d3.json("/get_data")]
  Promise.all(requests).then(function(response) {
    d3.select(".linechart").select("svg").remove();
    d3.select(".streamgraph").select("svg").remove();
    d3.select(".legend").select("svg").remove();
    if (chart == "streamgraph"){
      streamgraph(response)
    }
    else{
      linechart(response)
    }
  }).catch(function(e) {
      throw(e);
  });

}


function legend(keys, color, div, width, height){
  // set the dimensions and margins of the graph
  var margin_legend = {top: 10, right: 10, bottom: 0, left: 10},
  width_legend = width - margin_legend.left - margin_legend.right,
  height_legend = height - margin_legend.top - margin_legend.bottom;
  const legend_svg = d3.select(div)
                      .append('svg')
                      .attr("width", width_legend + margin_legend.left + margin_legend.right)
                      .attr("height", height_legend + margin_legend.top + margin_legend.bottom)
                      .append("g")
                      .attr("transform",
                      "translate(" + margin_legend.left + "," + margin_legend.top + ")");
  const g = legend_svg.append("g")
    .selectAll("g")
    .data(keys)
    .join("g")
      .attr("transform", (d, i) => `translate(${margin_legend.left},${i * 20})`);

  g.append("rect")
      .attr("width", 19)
      .attr("height", 19)
      .attr("fill", color);

  g.append("text")
      .attr("x", 24)
      .attr("y", 9.5)
      .attr("dy", "0.35em")
      .text(d => d);

}
