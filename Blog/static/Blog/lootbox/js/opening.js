document.addEventListener('DOMContentLoaded', function () {

  const DURATION = 10000;
  var box_id = document.getElementById('box_id').getAttribute('box_id');
  console.log("box id : ", box_id);
  const csrftoken = document.querySelector('meta[name="csrf-token"]').content;  
  let probas;

  
  function make_cum_probas(probas) {
    const cum_probas = [];
    let s = 0;
  
    for (let i = 0; i < probas.length; i++) {
      s += probas[i];
      cum_probas.push(s)
    }

    return cum_probas;
  }


  function choice(skins, cum_probas) {
    random = Math.random();
    for (let i = 0; i < cum_probas.length; i++) {
      if (random < cum_probas[i]) {
        return skins[i];
      }
    }
  
  }
  



  function startRoll(win_id){
    
    console.log('winId : ', win_id);

    $("#openCase").css("display", "none");

    var lineArrays = ['6905','6945','6985','7025','7065'];

    var landLine = lineArrays[Math.floor(Math.random() * lineArrays.length)];
    console.log(landLine);

    $(".itemBoxAn").animate(
      {right: landLine},
            {
              duration: DURATION,
              easing: 'easeOutQuint'
            }
    );

    
    fetch('/lootbox/drop_item', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
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
        setTimeout(function() {
            window.location.href = '/inventory';
        }, DURATION);
    })
    .catch(error => console.error('Erreur:', error));  // Gestion des erreurs
 }

  



  function replaceContent() {
    // Suppression du contenu actuel et insertion du nouveau
    
    $.ajax({
      url: '/lootbox/open',  // Assure-toi que l'URL correspond à la route que tu as définie
      type: 'GET',
      headers: { 'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
       },
      success: function(data) {
          // Remplacer le contenu du body par le nouveau contenu
          $('body').html(data);
          probas = JSON.parse(document.getElementById('data').getAttribute('probas'));
          var win_id = itemAttr();
          startRoll(win_id);
          
      },
      error: function(xhr, status, error) {
          console.error('Une erreur est survenue :', error);
      }
    });

    // Appliquer le CSS si nécessaire ou lier un autre fichier CSS dynamiquement
  
    document.getElementById('css_1').remove();
    
    
    // link.rel = 'stylesheet';
    // link.href = '/static/Blog/lootbox/css/opening.css'; // Remplacer par ton fichier CSS
    // document.head.appendChild(link);
  }

  function itemAttr(){
    var items = $(".itemBoxAn");
    var img_array = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'];

    var cum_probas = make_cum_probas(probas);
    console.log(cum_probas);

    var win_id = choice(img_array, cum_probas);
    var skins = document.getElementById('data').getAttribute('skins');
    skins = skins.replace(/'/g,"\"");
    var rarity_colors = document.getElementById('data').getAttribute('rarity-colors');
    rarity_colors = rarity_colors.replace(/'/g,"\"");
    rarity_colors = JSON.parse(rarity_colors);
    
    skins = JSON.parse(skins);
    console.log("skins : ", skins[0]);
    console.log("win_id : ", win_id);
    
    

    items.each(function() {
      // si l'item est l'objet itemBoxAnW, on ne fait rien
      if($(this).hasClass('itemBoxAnW')){
        
        $(this).append('<img src="' + skins[win_id - 1]+'" alt="'+win_id+'">');
        $(this).css('--RarityBorder', `10px solid ${rarity_colors[win_id - 1]}`);
      }
      else{
        var random = choice(img_array, cum_probas);
        $(this).append('<img src="' + skins[random - 1]+'" alt="'+random+'">');
        $(this).css('--RarityBorder', `10px solid ${rarity_colors[random - 1]}`);
      }
    });
    
    return win_id;
  }

  console.log('départ');
  var button = document.getElementById('button');
  const can_open = button.getAttribute('can-open');
  console.log(can_open);
  
  if (can_open === 'False') {
    button.style.backgroundColor = '#888888bb';
    }


  button.addEventListener('click', function(){
    if (can_open === 'True') {
      replaceContent();
    }
        
    });
});


