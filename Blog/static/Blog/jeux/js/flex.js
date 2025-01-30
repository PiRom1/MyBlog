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
    let end;
    let timer;
    let times = [];
    let time = 0;
    let value;
    let jeu_fini = false;

    let nb_serie = 3;
    let nb = 0;


    function debut_jeu() {
        // HTML shape
        document.body.innerHTML = '<h1> Attendez ... </h1>';
        document.body.style.backgroundImage = 'url()';
        document.body.style.height= '100px';
        document.body.style.backgroundColor = 'white';

        // Set variables
        game_begin = true;
        wait_for_click = false;
        early = true;
        value = getRandomInt(2, 5);
        
        // Launch timer
        timer = setInterval(() => {
            value -= 0.01; // Réduit la valeur de "step"
            if (value <= 0) {
                // Stoppe le timer lorsqu'il atteint 0
                clearInterval(timer); 
                wait_for_click = true;
                early = false;
                document.body.style.backgroundColor = 'green';
                document.body.innerHTML = '<h1> Cliquez ! </h1>';
                begin = Date.now();
              }
          }, 10);
    }


    function fin_jeu() {
        // HTML
        const mean_time = (time/nb).toFixed(2)
        document.body.innerHTML = `<h1>Temps moyen : ${mean_time}ms </h1><br><h2>Vos temps : ${times}</h2>`;

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

        
        // Write score in database
        const url = '/jeux/record';

        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest', // Ajoute cet en-tête pour indiquer qu'il s'agit d'une requête AJAX
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({game: 'Flex', score: mean_time})  // Envoie des données dans le corps de la requête
            })        
        .then(response => response.json())
        .then(data => {
            console.log("Donnée bien enregistrée !");
            })
    };



    bouton.addEventListener('click', async function(e) {
        e.stopPropagation();
        debut_jeu();
    });
    
    

    document.addEventListener('click', function(e) {
        if (game_begin) {
            if (early && !jeu_fini) {
                // If too soon click
                jeu_fini = true;
                clearInterval(timer);

                // HTML
                document.body.style.backgroundColor = 'red';
                document.body.innerHTML = `<h1>Stop clic FDP</h1>`;
                
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

                // Write score to database
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

            if (wait_for_click && !jeu_fini) {
                // Compute time
                end = Date.now();
                time += (end - begin);
                times.push(end-begin);
                nb += 1;

                if (nb >= nb_serie) {
                    jeu_fini = true;
                    fin_jeu();
                }
                else {
                    debut_jeu();
                }
                

            }
        }
            
        

    });

            
        
});