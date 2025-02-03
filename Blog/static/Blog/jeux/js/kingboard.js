document.addEventListener('DOMContentLoaded', async function () {
    // Récupérer le CSRF token depuis le meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const bouton = document.getElementById('bouton');
    let randomChar;
    const nb_char = 10;
    let step = 1;
    let begin, end, time;

    async function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async function draw_decompte() {
        let h1 = document.createElement('h1');
        h1.style.position = 'absolute';
        h1.style.top = '10%';
        h1.style.left = '50%';
        h1.innerHTML = '<h1>1 ...</h1>';
        document.body.appendChild(h1);
        await sleep(1000);
        h1.innerHTML = '';
        randomChar = String.fromCharCode(97 + Math.floor(Math.random() * 26));
        afficher_char();
        begin = Date.now();

    };
    
    bouton.addEventListener('click', function() {
        document.body.innerHTML = '';
        draw_decompte();
    })

    function afficher_char() {
        document.body.innerHTML = `<div class='char'>${randomChar}</div>`;
    }


    function draw_fail() {
        randomChar = null;
        document.body.innerHTML = `<h1>C'est si compliqué que ça d'appuyer sur les bonnes touches ?<br>T'iras pas bien loin dans l'informatique ... </h1>`;
        document.body.style.backgroundImage = 'url()';
        document.body.style.background = 'red';


        const replay = document.createElement("button");
        replay.style.display = "block";
        replay.style.margin = "0 auto";
        replay.style.textAlign = "center";
        replay.textContent = "Rejouer !";

        replay.addEventListener("click", function() {
            window.location.href='/jeux/Kingboard';
        });

        document.body.appendChild(replay);

        const link = document.createElement('a');
        link.href = '/jeux';
        link.textContent = 'Retour à la liste de jeux.';
        link.style.position = 'absolute';
        link.style.left = '5px';
        link.style.top = '10px';
        document.body.appendChild(link); 
    }

    function draw_end() {
        document.body.innerHTML = `<h1>Pas fou, tu as écrit ces ${nb_char} lettres en ${time} secondes ...</h1>`;
        document.body.style.backgroundImage = 'url()';
        document.body.style.background = 'green';

        
        const replay = document.createElement("button");
        replay.style.display = "block";
        replay.style.margin = "0 auto";
        replay.style.textAlign = "center";
        replay.textContent = "Rejouer !";

        replay.addEventListener("click", function() {
            window.location.href='/jeux/Kingboard';
        });

        document.body.appendChild(replay);

        const link = document.createElement('a');
        link.href = '/jeux';
        link.textContent = 'Retour à la liste de jeux.';
        link.style.position = 'absolute';
        link.style.left = '5px';
        link.style.top = '10px';
        document.body.appendChild(link); 

        // Imputation

        
        // Write score in database
        const url = '/jeux/record';

        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest', // Ajoute cet en-tête pour indiquer qu'il s'agit d'une requête AJAX
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({game: 'Kingboard', score: time})  // Envoie des données dans le corps de la requête
            })        
        .then(response => response.json())
        .then(data => {
            console.log("Donnée bien enregistrée !");
            })


    }

    
    document.addEventListener('keydown', function(e) {
        if (randomChar) {
            if (step < nb_char) {
                console.log(e.key, randomChar);
                if (e.key === randomChar) {
                    step += 1;
                    randomChar = String.fromCharCode(97 + Math.floor(Math.random() * 26));
                    afficher_char();
                }
                else {
                    draw_fail();
                }
            }
            else {
                end = Date.now();
                time = (end - begin)/1000;
                randomChar = null;
                draw_end();
            }
            
        }
        
    });

});