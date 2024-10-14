$(document).ready(function(){
  // itemAttr();
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

  var lineArrays = ['6905','6945','6985','7025','7065'];

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

function itemAttr(){
  var item = $(".itemBoxAn");
  var img_array = ['1'];
  for (var i = 0; i < item.length; i++) {
    item[i].append('<img src="/static/Blog/lootbox/img/1.png" />');
  }    
  console.log(item);
}
