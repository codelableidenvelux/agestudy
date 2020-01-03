function read_csv(filename){
var txtFile = new XMLHttpRequest();
txtFile.onload = function() {
    allText = txtFile.responseText;
    allTextLines = allText.split(/\r\n|\n/);

    for(var i = 0; i < allTextLines.length; i++) {
        document.body.innerHTML += allTextLines[i];
        document.body.innerHTML += '<br/>';
    }
}

txtFile.open("get", filename, true);
txtFile.send();
}
