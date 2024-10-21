document.addEventListener('DOMContentLoaded', function () {


  var box_id = document.getElementById('box_id').getAttribute('box_id');
  console.log("box id : ", box_id);
  const csrftoken = document.querySelector('meta[name="csrf-token"]').content;  
function startRoll(win_id){
  
  console.log('winId : ', win_id);

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
    fetch('/lootbox/drop_item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken  // Récupération du token CSRF
        },
        body: JSON.stringify({ item: win_id, box_id: box_id})  // Envoie l'item dans le corps de la requête
    })
    .then(response => {
        // Vérifie si la réponse est correcte
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        // Redirection après une réponse réussie
        window.location.href = '/inventory_2';
    })
    .catch(error => console.error('Erreur:', error));  // Gestion des erreurs
}, 1000);
   

}

function itemAttr(){
  var items = $(".itemBoxAn");
  var img_array = ['1','2','3'];//, '4', '5', '6', '7', '8', '9', '10', '11'];
  var win_id = img_array[Math.floor(Math.random() * img_array.length)];
  items.each(function() {
    // si l'item est l'objet itemBoxAnW, on ne fait rien
    if($(this).hasClass('itemBoxAnW')){
      
      $(this).append('<img src="/static/Blog/lootbox/box1/'+win_id+'.png" alt="'+win_id+'">');
    }
    else{
      var random = img_array[Math.floor(Math.random() * img_array.length)];
      $(this).append('<img src="/static/Blog/lootbox/box1/'+random+'.png" alt="'+random+'">');
    }
  });


  return win_id;
  

}



function replaceContent() {
  // Suppression du contenu actuel et insertion du nouveau
  
  $.ajax({
    url: '/lootbox/open',  // Assure-toi que l'URL correspond à la route que tu as définie
    type: 'GET',
    success: function(data) {
        // Remplacer le contenu du body par le nouveau contenu
        $('body').html(data);

        win_id = 

        win_id = itemAttr();
        startRoll(win_id);
        
    },
    error: function(xhr, status, error) {
        console.error('Une erreur est survenue :', error);
    }
});

  // Appliquer le CSS si nécessaire ou lier un autre fichier CSS dynamiquement
 
  document.getElementById('css_1').remove();
  
  
  // link.rel = 'stylesheet';
  // link.href = '/static/Blog/lootbox/css/openning.css'; // Remplacer par ton fichier CSS
  // document.head.appendChild(link);
}



  console.log('départ');
  var button = document.getElementById('button');
  button.addEventListener('click', function(){
    replaceContent();
    });
});


