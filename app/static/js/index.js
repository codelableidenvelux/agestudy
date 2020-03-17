// Onclick of the checkboxes check if all the minimum requirements are met (if all boxes checked), if they are then dissplay the register form
function onClickPC(){
  if (document.getElementById("pc").checked){
    if (document.getElementById("task_switching_button")){
        document.getElementById("task_switching_button").style.display = "block";
    };
    if (document.getElementById("corsi_button")){
      document.getElementById("corsi_button").style.display = "block";
    };
    if (document.getElementById("n_back_button")){
      document.getElementById("n_back_button").style.display = "block";
    };
    if (document.getElementById("sf_36_button")){
      document.getElementById("sf_36_button").style.display = "block";
    };
    if (document.getElementById("phone_survey_button")){
          document.getElementById("phone_survey_button").style.display = "block";
    };
    if (document.getElementById("button_task")){
          document.getElementById("button_task").style.display = "block";
    };
  }
  else{
    if (document.getElementById("task_switching_button")){
        document.getElementById("task_switching_button").style.display = "none";
    };
    if (document.getElementById("corsi_button")){
      document.getElementById("corsi_button").style.display ="none";
    };
    if (document.getElementById("n_back_button")){
      document.getElementById("n_back_button").style.display = "none";
    };
    if (document.getElementById("sf_36_button")){
      document.getElementById("sf_36_button").style.display = "none";
    };
    if (document.getElementById("phone_survey_button")){
          document.getElementById("phone_survey_button").style.display = "none";
    };
    if (document.getElementById("button_task")){
          document.getElementById("button_task").style.display = "none";
    };
  }
};
