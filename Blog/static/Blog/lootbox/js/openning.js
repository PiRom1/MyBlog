document.addEventListener('DOMContentLoaded', function () {


  
function startRoll(){
  replaceContent();
  item = itemAttr();
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



  setTimeout(function(){
    console.log('fini :', item);
}, 10000);

  

}

function itemAttr(){
  var items = $(".itemBoxAn");
  var img_array = ['1','2','3'];
  items.each(function() {
      var random = img_array[Math.floor(Math.random() * img_array.length)];
      $(this).append('<img src="/static/Blog/lootbox/box1/'+random+'.png" alt="'+random+'">');
  });
  console.log(items);

  var item = $(".itemBoxAnW");
  item.append('<img src="/static/Blog/lootbox/box1/3.png" alt="3">');
  console.log(item.src);
  

}



function replaceContent() {
  // Suppression du contenu actuel et insertion du nouveau
  document.body.innerHTML = `
     <div class="blurred-background"></div>

    <div class="container-fluid content">
      <div class="row">
        <button type="button" id="openCase" class="btn btn-info copenbtn"> OPEN </button>
        <div class="container-fluid caseOpeningArea">
          <div class="row">
            <div  class="container animationAreaItems">
              <div class="row">
                <div class="row text-center flex-nowrap mx-auto">
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn itemBoxAnW"> </div>  
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                  <div class="itemBoxAn"> </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    <!-- <div class="focus-area"></div>  -->`

  // Appliquer le CSS si nécessaire ou lier un autre fichier CSS dynamiquement
  var link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = '/static/Blog/lootbox/css/openning.css'; // Remplacer par ton fichier CSS
  document.head.appendChild(link);
}



  console.log('départ');
  var button = document.getElementById('button');
  button.addEventListener('click', startRoll);
});


