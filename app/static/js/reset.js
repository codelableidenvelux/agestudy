var password = document.getElementById("password");
console.log(password)
// this starts as soon as user types something in
password.onkeyup = function() {
    // Validate numbers
    var numbers = /[0-9]/g;
    if (document.getElementById("password").value.match(numbers)) {
        document.getElementById("message_number").style.display = "none";
    } else {
        document.getElementById("message_number").style.display = "block";
    }

    // Validate length
    if (document.getElementById("password").value.length >= 5) {
        document.getElementById("message_length").style.display = "none";
    } else {
        document.getElementById("message_length").style.display = "block";
    }
}
