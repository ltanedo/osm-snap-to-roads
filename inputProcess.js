var coord;
document.getElementById('file').onchange = function(){

  var file = this.files[0];

  var reader = new FileReader();
  reader.onload = function(progressEvent){
    // Entire file
    
    var count=0;

    // By lines
    var lines = this.result.split('\n');
    for(var line = 0; line < lines.length; line++){
    
        count=count+1;
      var lat=lines[line].replace(/"/g, '').split(',')[2];
        var long=lines[line].replace(/"/g, '').split(',')[3]
        if(count==99){
            coord= coord+lat;
            coord=coord+ ',';
            coord=coord+long;
            coord=coord.replace("undefinedlat,lon|", '');
            console.log(coord);
           break;

        }
        else{
           coord= coord+lat;
           coord=coord+ ',';
           coord=coord+long;
           coord=coord+'|';
        }
  
        
    }

  };
  reader.readAsText(file);
};
