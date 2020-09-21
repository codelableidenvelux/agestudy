function transportation_ammount(){
  var radios = document.getElementsByName('transportation');
  var cost = document.getElementById('transportation_cost_div');
  for (var i = 0, length = radios.length; i < length; i++) {
    if (radios[i].checked) {
      // do whatever you want with the checked radio
      if (radios[i].value === "No"){
        cost.style.display = "none"
      }
      else{
        cost.style.display = "block"
      }

      // only one radio can be logically checked, don't check the rest
      break;
    }
  }
}
