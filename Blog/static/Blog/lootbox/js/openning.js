$(document).ready(function(){
  $("#openCase").click(function(){


    if ($(this).hasClass('disabled')) {
        return false;
    } else {
         startRoll();
    }

  });
});


function startRoll(){

  $("#openCase").css("display", "none");

  var lineArrays = ['6725px','6765px','6805px','6845','6885'];

  var landLine = lineArrays[Math.floor(Math.random() * lineArrays.length)];
  console.log(landLine);

  $(".itemBoxAn").animate(
    {right: landLine},
          {
            duration: 10000,
            easing: 'easeOutQuint'
          }
  );
}
