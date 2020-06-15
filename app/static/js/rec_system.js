
f_promo_code.onkeyup = function(){
  $.getJSON("/check_promo_code", {'f_promo_code': f_promo_code.value}, function(result, state){
    if (state === "success"){
      if (!result){
        $("#f_promo_code").removeClass("is-invalid");
        $('#f_promo_code_button').removeAttr('disabled');

      } else {
        $("#f_promo_code").addClass("is-invalid");
        $('#f_promo_code_button').attr('disabled', 'disabled');
      }
    }
  });
}
