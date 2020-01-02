//This script was written with help from https://www.w3schools.com/howto/howto_js_password_validation.asp :D -->

///////////////////////////////////////////////////////////////////////////
//////////////////////// Check the password  ///////////////////////////////
///////////////////////////////////////////////////////////////////////////
var password = document.getElementById("password");
var letter = document.getElementById("message_letter");
var capital = document.getElementById("message_capital");
var number = document.getElementById("message_number");
var length = document.getElementById("message_length");

// this starts as soon as user types something in
password.onkeyup = function() {
    // Validate lowercase letters
    var lower_letters = /[a-z]/g;
    if (password.value.match(lower_letters)) {
        document.getElementById("message_letter").style.display = "none";
    } else {
        document.getElementById("message_letter").style.display = "block";
    }

    // Validate capital letters
    var upper_letters = /[A-Z]/g;
    if (password.value.match(upper_letters)) {
        document.getElementById("message_capital").style.display = "none";
    } else {
        document.getElementById("message_capital").style.display = "block";
    }

    // Validate numbers
    var numbers = /[0-9]/g;
    if (password.value.match(numbers)) {
        document.getElementById("message_number").style.display = "none";
    } else {
        document.getElementById("message_number").style.display = "block";
    }

    // Validate length
    if (password.value.length >= 5) {
        document.getElementById("message_length").style.display = "none";
    } else {
        document.getElementById("message_length").style.display = "block";
    }
}

///////////////////////////////////////////////////////////////////////////
//////////////////////// Show other checkbox //////////////////////////////
///////////////////////////////////////////////////////////////////////////
var collect_possible_id = document.getElementById("collect_possible_id");
var money = document.querySelector("input[name=money]");
var collect_possible = document.querySelector("input[name=collect_possible]");

// if the first checkbox (want to participate for money) was selected
// display the other checkbox (collect possible)
money.addEventListener( 'change', function() {
if(this.checked) {
    collect_possible_id.style.display = "block";
  } else {
    collect_possible_id.style.display = "none";
  }
});
///////////////////////////////////////////////////////////////////////////
//////////////////////// SET THE DATE /////////////////////////////////////
///////////////////////////////////////////////////////////////////////////
// Source: https://formden.com/blog/date-picker
// Get todays date
var today = new Date();
var dd = String(today.getDate()).padStart(2, '0');
var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
var yyyy = today.getFullYear();

today = yyyy + '-' + mm + '-' + dd;

// Date picker with jquery and bootstrap
$(document).ready(function() {
    var date_input = $('input[name="date"]'); //our date input has the name "date"
    var container = $('.bootstrap-iso form').length > 0 ? $('.bootstrap-iso form').parent() : "body";
    date_input.datepicker({
        format: 'yyyy-mm-dd',
        container: container,
        todayHighlight: true,
        autoclose: true,
        startDate: "1900-01-01",
        endDate: today
    })
})
/////////////////////////////////////////////////////////////////////////
////////////////////// client side validation ///////////////////////////
/////////////////////////////////////////////////////////////////////////
// change class from invalid to valid

// This function takes the variable input,
// input is an id from an input form from the html page
// It also takes an array of functions that return bools
// these functions are conditions that the input has to adhere to
// if atleast one of the functions return true, then the input is wrong
// show the feedback for invalid
// else show feedback for valid "looks good"
// this function is called onkeyup
valid_invalid = function(input, functions){
  var input_var = $(input);
  input_var.keyup(function(){
  if (functions.some(function(f){ console.log(f())
    return f()})){
    input_var.addClass("is-invalid");
    input_var.removeClass("is-valid");
  } else {
    input_var.addClass("is-valid");
    input_var.removeClass("is-invalid");
  }
});
}

// they return true if there is an incorrect/invalid input
// checks if there are any whitespace characters in username
var whitespace = () => document.getElementById("username").value.match(/\s/g);
// checks if the lentgh of username is smaller than 5
var length_username = () => document.getElementById("username").value.length <= 5;
valid_invalid("#username", [whitespace, length_username])

// they return true if there is an incorrect/invalid input
// check if the email does not have an @
var have_at = () => !document.getElementById("email").value.match(/[@]/g);
// check if the email length is 0
var length_email = () => document.getElementById("email").value.length < 1;
valid_invalid("#email", [have_at, length_email])

// return true if there is an incorrect/invalid input
// check if a value is not chosen
var choose_gender = () => !document.getElementById("gender").value;
valid_invalid("#gender", [choose_gender])

// TODO: BUG HERE
// return true if there is an incorrect/invalid input
// check if the input is not a real date

var valid_date = () => !Date.parse(document.getElementById("date").value);
function valid_date(){
  date = document.getElementById("date").value
  console.log(Date.parse(date))
  return !Date.parse(date)
}
valid_invalid("#date", [valid_date])

// since the date function autofills if the date was filled incorrectly
// it fills in a correct date
// you must check if the date is valid and remove the invalid-feedback onblur
date = $("#date")
date.blur(function(){
  if (!valid_date()){
    date.addClass("is-valid");
    date.removeClass("is-invalid");
  } else {
    date.addClass("is-invalid");
    date.removeClass("is-valid");
  }
})

// this function checks if the username is already in use
// it goes to the /availability url and performs the python function in application.py
// the function essentially checks the database to see if the username already exists
// it returns false if the username is in use and true if its available
// this function happens onblur so after the user has finished typing a password and clicked somewhere else
// afterwards getjson calls a function that has two parameters the result (true or false) and the state,
// success indicates it was able to get the boolean,
// if it succeeded change the username to valid if all conditions are met
//  conditions are : availability, length>5 and no whitespace characters
username.onblur = function(){
  $.getJSON("/availability", {'username': username.value}, function(result, state){
    if (state === "success"){
      if (result && !length_username() && !whitespace()){
        $("#username").addClass("is-valid");
        $("#username").removeClass("is-invalid");
      } else {
        $("#username").addClass("is-invalid");
        $("#username").removeClass("is-valid");
      }
    }
  });
}
