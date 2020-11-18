function myFunction() {
 
    var x = document.getElementById("otp");
    var y = document.getElementById("vehicle_number");
  
    if (x.style.display === "none") {
      if(y.value.length != 0){
        x.style.display = "block";
      }
      else{
        alert("Enter Vehicle Number First");
      }
    } else {
      x.style.display = "none";
    }
  }

function sumbit(){
  var x = document.getElementById("otp");
  var y = document.getElementById("vehicle_number");
  var y = document.getElementById("otp_value");
  if(y.value.length != 0){
    e = "click"
    e.preventDefault()
    alert("enter vehicle number First")  
  }

}

function mySubmitFunction(e) {
  e.preventDefault();
  var x = document.getElementById("otp");
    var y = document.getElementById("vehicle_number");
  
    if (x.style.display === "none") {
      if(y.value.length != 0){
        x.style.display = "block";
      }
      else{
        alert("Enter Vehicle Number First");
        return false;
      }
    } else {
      x.style.display = "none";
      // return true
    }
  return true;
}



