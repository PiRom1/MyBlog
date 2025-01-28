document.addEventListener('DOMContentLoaded', async function () {
// Récupérer le CSRF token depuis le meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    function getRandomInt(min, max) {
        return min + Math.floor(Math.random() * (max-min));
      }

    const bouton = document.getElementById('bouton');
    
    let game_begin = false;

    let early = true;
    let wait_for_click = false;
    let begin;
    let timer;

    bouton.addEventListener('click', async function(e) {
        e.stopPropagation();
        game_begin = true;
        document.body.innerHTML = '<h1> Attendez ... </h1>';
        document.body.style.backgroundImage = 'url()';
        document.body.style.height= '100px';
        document.body.style.backgroundColor = 'white';
        
        let value = getRandomInt(2, 5);
        
        timer = setInterval(() => {
            console.log("value : ", value);
            value -= 0.01; // Réduit la valeur de "step"
            if (value <= 0) {
                clearInterval(timer); // Stoppe le timer lorsqu'il atteint 0
                wait_for_click = true;
                early = false;
                document.body.style.backgroundColor = 'green';
                document.body.innerHTML = '<h1> Cliquez ! </h1>';
                begin = Date.now();
              }
          }, 10);

        });
    
    document.addEventListener('click', function(e) {
        if (game_begin) {
            if (wait_for_click) {
                
                const end = Date.now();
                const time = end - begin;
                document.body.innerHTML = `<h1>Time : ${time}ms </h1>`;
                wait_for_click = false;

                const bouton = document.createElement("button");
                bouton.style.display = "block";
                bouton.style.margin = "0 auto";
                bouton.style.textAlign = "center";
                bouton.textContent = "Rejouer !";

                bouton.addEventListener("click", function() {
                    window.location.href='/jeux/Flex';
                });

                document.body.appendChild(bouton);

                const link = document.createElement('a');
                link.href = '/jeux';
                link.textContent = 'Retour à la liste de jeux.';
                link.style.position = 'absolute';
                link.style.left = '5px';
                link.style.top = '10px';
                document.body.appendChild(link); 

                
                    
                const url = '/jeux/record';

                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest', // Ajoute cet en-tête pour indiquer qu'il s'agit d'une requête AJAX
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({game: 'Flex', score: time})  // Envoie des données dans le corps de la requête
                    })        
                .then(response => response.json())
                .then(data => {
                    console.log("Donnée bien enregistrée !");
                    })
                
                

            }
            if (early) {
                document.body.style.backgroundColor = 'red';
                document.body.innerHTML = `<h1>Stop clic FDP</h1>`;
                clearInterval(timer); // Stoppe le timer lorsqu'il atteint 0
                const link = document.createElement('a');
                link.href = '/jeux';
                link.textContent = 'Retour à la liste de jeux.';
                link.style.position = 'absolute';
                link.style.left = '5px';
                link.style.top = '10px';
                document.body.appendChild(link);

                const bouton = document.createElement("button");
                bouton.style.display = "block";
                bouton.style.margin = "0 auto";
                bouton.style.textAlign = "center";
                bouton.textContent = "Rejouer !";
                bouton.addEventListener("click", function() {
                    window.location.href='/jeux/Flex';
                });
                document.body.appendChild(bouton); 

                // Add data to database
                const url = '/jeux/record';

                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest', // Ajoute cet en-tête pour indiquer qu'il s'agit d'une requête AJAX
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({game: 'Flex', score: 9999})  // Envoie des données dans le corps de la requête
                    })        
                .then(response => response.json())
                .then(data => {
                    console.log("Donnée bien enregistrée !");
                    })


                }
        }
        

    });
            
        
    });