window.onload = function()
{
  var requests = [d3.json("/get_data")]
  Promise.all(requests).then(function(response) {
    stacked_barchart(response, 'tasks')
    // streamgraph(response)
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

function preview_bb_msg(){
  var bb_msg_title = document.getElementById("bb_msg_title")
  d3.select(".bb_board_title").text(bb_msg_title.value)
  var bb_msg = document.getElementById("bb_msg")
  d3.select(".bb_board_msg").text(bb_msg.value)
  d3.select(".length_text").text(bb_msg.value.length + "/500")
}

function basic_info(response){
  var data = response[0]["basic_stats"]
   d3.select(".num_p")
     .text("Number of participants: " + data["num_p"]);

    d3.select(".num_active_p")
      .text("Number of active participants: " + data["num_active_p"]);

    d3.select(".n_p_ids")
      .text("Number of participation ids: " + data["n_p_ids"]);
}

function toggle_charts(chart){
  var requests = [d3.json("/get_data")]
  Promise.all(requests).then(function(response) {
    d3.select(".stacked_barchart").select("svg").remove();

    stacked_barchart(response, chart)

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

// parse the date / time
var parseTime = d3.timeFormat("%d-%b-%Y");

function get_task_type(task_id){
  var task = ""
  if (task_id === 1){
    task = "cor"
  }
  else if (task_id === 2){
    task = "nb"
  }
  else if (task_id === 3){
    task = "ts"
  }
  else if (task_id === 4){
    task = "sf"
  }
  else if (task_id === 5){
    task = "ps"
  }
  else{
    task = "rt"
  }
  return task
}
function process_timeline_data(sign_up, tasks){
  timeline_data = [{"id":0, "date":sign_up, "type": "sign_up"}]
  for (i in tasks){
    timeline_data.push({"id":parseInt(i)+1, "date":new Date(tasks[i][0]), "type":get_task_type(tasks[i][1])})
  }
  return timeline_data
}


function select_user_ajax(){
  $.getJSON("/select_user", {'username': username.value, 'user_id': user_id.value, 'participation_id': participation_id.value, 'view_user_payment_bar' : view_user_payment_bar.checked}, function(result, state){
    if (state === "success"){
      if (Object.keys(result).length != 0){
        var user = result["user"];
        var tasks = result["tasks"];
        var payment = result["payment"];

        var birthdate = new Date(user["birthdate"])
        var sign_up =  new Date(user['time_sign_up'])
        //var timeline_data = process_timeline_data(sign_up, tasks)
        //timeline_chart(timeline_data)
        d3.select(".user").html('<b>User_id:</b> '+ user["user_id"] +
                    '<br> <b>Email:</b> ' + user["email"] +
                    '<br> <b>Gender:</b> ' + user["gender"] +
                    '<br> <b>Birthdate:</b> '+ parseTime(birthdate) +
                    '<br> <b>User_type:</b> ' + user["user_type"] +
                    '<br> <b>Participation_id:</b> ' + user["participation_id"] +
                    '<br> <b>Time_sign_up:</b> ' +  parseTime(sign_up) +
                    '<br> <b>Admin:</b> ' + user['admin'] +
                    '<br> <b>Psytoolkit_id:</b> ' + user['psytoolkit_id'] +
                    '<br> <b>Consent:</b> ' + user['consent'] +
                    '<br> <b>Credits participant:</b> ' + user['credits_participant'] +
                    '<br> <b>Promo code:</b> ' + user['promo_code'] +
                    '<br> <b>Duplicate ID:</b> ' + user['duplicate_id'] +
                    '<br> <b>Can collect payment:</b> ' + user['can_collect_payment'] +
                    '<br> <b>Date of last collection:</b> ' + user['date_collected'])

      d3.select("#barChart").select('svg').remove();
      d3.select("#barChart").select('h1').remove();
      d3.select("#barChart").select('p').remove();
      if (user["user_type"] == 1 && document.getElementById("view_user_payment_bar").checked){
        d3.select("#barChart").append('h1').text('Payment Info')
        var price = payment[0]
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
        var data = [{"name": "€",
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
          "color": "#ff7632"}]
        // make the barchart by calling the barchart function
        barChart(data)}
        else if (user["user_type"] == 2  && document.getElementById("view_user_payment_bar").checked ){
          d3.select("#barChart").append('h1').text('Payment Info')
          d3.select("#barChart").append('p').text('User not participating for payment')
        };
        d3.select(".tasks_table").html(pretty_print_tasks(tasks))
      }
      }
      else{
        d3.select(".user").text('No user found')
      }
  });
}

function change_user_ajax(value){
  $.getJSON("/change_user", {'change_user_id': change_user_id.value, 'change_participation_id': change_participation_id.value, 'value': value}, function(result, state){
    if (state === "success"){
      if (change_user_id.value){
        d3.select('.feedback_db_change').text(result + ": " + value + " for participant: " + change_user_id.value)
      }
      else{
        d3.select('.feedback_db_change').text(result + ": " + value + " for participant: " + change_participation_id.value)
      }
    }
  });
}

function duplicate_user_ajax(value){
  $.getJSON("/duplicate_user_ajax", {'p_id_1': p_id_1.value, 'p_id_2': p_id_2.value}, function(result, state){
    if (state === "success"){
        d3.select('.feedback_db_duplicate').text(result)
    }
  });
}


function clear_selection(){
  d3.selectAll('.selection').text("")
}

function clear_timelines(){
  d3.selectAll('.timeline_chart').select("svg").remove();
}

function pretty_print_users(data){
  users = ""
  for (data_item in data){
  var birthdate = new Date(data[data_item][3])
  var sign_up =  new Date(data[data_item][6])

  var user_id = `<td> ${data[data_item][0]} </td>`
  var participation_id = `<td> ${data[data_item][5]} </td>`
  var gender = `<td> ${data[data_item][2]} </td>`
  var birthdate = `<td> ${parseTime(birthdate)} </td>`
  var time_sign_up = `<td> ${parseTime(sign_up)} </td>`
  var user_type = `<td> ${data[data_item][4] } </td>`
  var consent = `<td> ${data[data_item][8] } </td>`
  var credits_participant = `<td> ${data[data_item][9] } </td>`
    users = users + `<tr> ${user_id} ${participation_id}  ${gender} ${birthdate} ${time_sign_up} ${user_type} ${consent} ${credits_participant}  <tr>`
  }
  html = `
  <table class=table_css style="width:100%">
              <tr>
                <th>User ID</th>
                <th>Participation ID</th>
                <th>Gender</th>
                <th>Birthdate</th>
                <th>Time sign up:</th>
                <th>User type</th>
                <th>Consent</th>
                <th>Credits participant</th>
              </tr>
              ${users}
          </table>`
  return html
}

function pretty_print_tasks(tasks){
  let task_table = ""
  var groups = []
  tasks = tasks.sort(function (a, b) {
      return new Date(b[0]) - new Date(a[0]);
    });
  var total_payout = 0;
  for (task in tasks){
    var task_id = tasks[task][1]
    var date_date_exec = new Date(tasks[task][0])
    var date_date_collected =  new Date(tasks[task][3])
    if (tasks[task][2]){
      var col = 'False'
    }
    else{
      var col = 'True'
    }
    var tasktype = get_task_type(task_id)
    if (tasktype == 'cor' || tasktype == 'ts' || tasktype == 'nb'){
      task_id = 10
    }
    var id = date_date_exec.getFullYear().toString() + date_date_exec.getMonth().toString() + task_id.toString();
    if (!groups[id] && tasktype != 'ps' && tasktype != 'sf' && tasktype != 'rt')
    {
      var payment = '1.75'
      groups[id] = payment
    }
    else if (!groups[id] && tasktype == 'rt') {
      var payment = '0.25'
      groups[id] = payment
    }
    else if (tasktype == 'ps' || tasktype == 'sf' ){
      var payment = '2'
      groups[id] = payment
    }
    else{
      var payment = '0'
      groups[id] = payment
    }
    if (tasks[task][2]){
      total_payout = total_payout + parseFloat(payment)
      console.log(total_payout)
      console.log(parseFloat(payment))
    }

    var index = `<td> ${parseInt(task)+1} </td>`
    var date_exec = `<td> ${parseTime(date_date_exec)} </td>`
    var task_name = `<td> ${tasktype} </td>`
    var collected = `<td> ${col} </td>`
    var payment_col =  `<td> ${payment} </td>`
      task_table = task_table + `<tr> ${index} ${date_exec} ${task_name}  ${collected} ${payment_col}<tr>`
  }
  html = `<div class=table_scroll>
  <p> <b>Potential total:</b> ${total_payout} € </p>
  <table class=table_css style="width:100%;">
              <tr>
                <th>N</th>
                <th>Date performed</th>
                <th>Task type</th>
                <th>Collected payment</th>
                <th>Payment</th>
              </tr>
              ${task_table}
  </table>
  </div>`
  return html
}

function query_data_ajax(type){
  $.getJSON("/query_data", {'gender': gender.value, 'user_type': user_type.value, 'special_user' :special_user.value}, function(result, state){
    if (state === "success"){
      $('.query_dropdown option').prop('selected', function() {
        return this.defaultSelected;
      });
      if (Object.keys(result).length != 0){
        d3.select(".gender_p").html(pretty_print_users(result))
      }
      else{
        d3.select(".gender_p").text('No user found')
      }
    }
  });
}

function download_data_ajax(table){
  $.getJSON("/download_data", {'download_password': download_password.value, 'table_name': table}, function(results, state){
    if (state === "success"){
      // if the password is incorrect then flash a message, send user to top of page, fade out the message
      if (results === "Incorrect Password"){
        $('#flash').append('<header><div class="alert alert-primary border text-center" id="flash" role="alert">' + results + '</div></header>')
        $(document).ready(function(){
            $(this).scrollTop(0);
            setTimeout(function() {
              $('.alert').fadeOut('slow');}, 2000); // <-- time in milliseconds
        });
      }
      else{
      // convert json to csv and get the data in right format for the csv file
      const column_names = results[0];
      const result = results[1];
      const replacer = (key, value) => value === null ? '' : value // specify how you want to handle null values here
      const header = Object.keys(result[0])
      let csv = result.map(row => header.map(fieldName => JSON.stringify(row[fieldName], replacer)).join(','))
      csv.unshift(column_names.join(','))
      csv = csv.join('\r\n')

      // write to a file and download
      let csvContent = "data:text/csv;charset=utf-8," + csv;
      var encodedUri = encodeURI(csvContent);
      var link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      filename = table + ".csv"
      link.setAttribute("download",filename);
      document.body.appendChild(link); // Required for FF
      link.click();
      // reload so that they need to fill in password again to be able to download another file
      location.reload()
    }
  }
});
}

function download_active_inactive(table){
  $.getJSON("/download_active_inactive", {'download_ai_pass': download_ai_pass.value, 'table_name': table}, function(results, state){
    if (state === "success"){
      // if the password is incorrect then flash a message, send user to top of page, fade out the message
      if (results === "Incorrect Password"){
        $('#flash').append('<header><div class="alert alert-primary border text-center" id="flash" role="alert">' + results + '</div></header>')
        $(document).ready(function(){
            $(this).scrollTop(0);
            setTimeout(function() {
            $('.alert').fadeOut('slow');}, 2000); // <-- time in milliseconds
      });
      }
      else{
        // convert json to csv and get the data in right format for the csv file
        const column_names = 'Emails';
        const result = results;
        const replacer = (key, value) => value === null ? '' : value // specify how you want to handle null values here
        const header = Object.keys(result[0])
        let csv = result.map(row => header.map(fieldName => JSON.stringify(row[fieldName], replacer)).join(','))
        //csv.unshift(column_names.join(','))
        csv = csv.join('\r\n')

        // write to a file and download
        let csvContent = "data:text/csv;charset=utf-8," + csv;
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        filename = table + ".csv"
        link.setAttribute("download",filename);
        document.body.appendChild(link); // Required for FF
        link.click();
        // reload so that they need to fill in password again to be able to download another file
        location.reload()
    }
  }
});
}

function inactive_users_ajax(sort_by){
  $.getJSON("/inactive_users", {'n_weeks': n_weeks.value}, function(result, state){
    if (state === "success"){
      if (sort_by === "user_id"){
          result = result.sort();
      }
      else{
        result = result.sort(function (a, b) {
          return b[sort_by] - a[sort_by];
        });
      }

     $(".sort_by_inactive").text(sort_by);
      var inactive_participants_list = "";
      var d = new Date(0); // The 0 there is the key, which sets the date to the epoch
      for (i in result){
        time_exec = date_formating(result[i].time_exec)
        date_email_sent = date_formating(result[i].date_email_sent)
        var input_item = `<td><input type='checkbox' name=${i} value=${result[i].user_id}><label for=${i}>${JSON.stringify(result[i].user_id)}</label></td>`
        var p_id_item = `<td>${JSON.stringify(result[i].participation_id)}</td>`
        var reminder_item = `<td>${JSON.stringify(result[i].reminder)}</td>`
        var time_exec_item = `<td>${JSON.stringify(time_exec)}</td>`
        var email_sent_item = `<td>${JSON.stringify(result[i].should_email)}</td>`
        var date_email_sent_item = `<td>${JSON.stringify(date_email_sent)}</td>`
        inactive_participants_list = inactive_participants_list + `<tr> ${input_item} ${p_id_item} ${reminder_item} ${time_exec_item} ${email_sent_item} ${date_email_sent_item}</tr>`
      }
      html = `
      <table id="inactive_participants_table" style="width:100%">
                  <tr>
                    <th>User ID</th>
                    <th>Participation ID</th>
                    <th>Reminder</th>
                    <th>Last active (time_exec) <br/> dd/mm/yy </th>
                    <th>Should email</th>
                    <th>Date email sent <br/> dd/mm/yy </th>
                  </tr>
                  ${inactive_participants_list}
              </table>`
      d3.select(".inactive_users_form").html(html + '<input class="btn btn-primary" type="submit" value="Submit">')
    }
  });
  return false
}

function date_formating(date){
  if (date != null){
    date = new Date(date)
    var options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    date = date.toLocaleDateString("en-GB"); // 9/17/2016
  }
  return date
}
