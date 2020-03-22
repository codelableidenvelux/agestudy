window.onload = function(){
  if (document.getElementById("check_form")){
    if (document.getElementById("title").textContent != "Phone survey" &&  document.getElementById("title").textContent != "SF-36"){
      document.getElementById("check_form").style.display = "block"
    }
    else{
        document.getElementById("check_form").style.display = "none"
    }
  }

    if (document.getElementById("pc").checked){
      display_block()
    }
    else{
      display_none()
    }
}

// Onclick of the checkboxes check if all the minimum requirements are met (if all boxes checked), if they are then dissplay the register form
function onClickPC(){
  $.getJSON("/session_pc", {'checked': document.getElementById("pc").checked}, function(result, state){
    if (state === "success"){
      if (result){
        display_block()
      } else {
        display_none()
      }
    }
  });
};

function display_block(){
  if (document.getElementById("task_switching_button")){
      document.getElementById("task_switching_button").style.display = "block";
  };
  if (document.getElementById("corsi_button")){
    document.getElementById("corsi_button").style.display = "block";
  };
  if (document.getElementById("n_back_button")){
    document.getElementById("n_back_button").style.display = "block";
  };
  if (document.getElementById("button_task") && document.getElementById("title").textContent != "Phone survey" &&  document.getElementById("title").textContent != "SF-36" ){
    document.getElementById("button_task").style.display = "block";
  };
}

function display_none(){
  if (document.getElementById("task_switching_button")){
      document.getElementById("task_switching_button").style.display = "none";
  };
  if (document.getElementById("corsi_button")){
    document.getElementById("corsi_button").style.display ="none";
  };
  if (document.getElementById("n_back_button")){
    document.getElementById("n_back_button").style.display = "none";
  };
  if (document.getElementById("button_task") && document.getElementById("title").textContent != "Phone survey" &&  document.getElementById("title").textContent != "SF-36"){
    document.getElementById("button_task").style.display = "none";
  };
}
