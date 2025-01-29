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
        loadQuiz();
        const verifierReponsesButton = document.getElementById('verifierReponses');
        verifierReponsesButton.addEventListener('click', verifierReponses);
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

    function loadQuiz() {
        const container = document.body;
        container.innerHTML = `
          <h2 style="text-align:center; color:#0044cc;">Quiz de Compréhension</h2>
  
          <div class="question">
            <p><strong>1. Quelle est la toute première instruction dans les règles ?</strong></p>
            <div class="options" style="margin-left:20px;">
              <label>
                <input type="radio" name="q1" value="A">
                Dès que tu auras cliqué sur 'Commencer', prépare-toi à appuyer sur l'écran dès que celui-ci change de couleur.
              </label><br>
              <label>
                <input type="radio" name="q1" value="B">
                Dès que tu auras cliqué sur 'Commencer', prépare-toi à cliquer sur l'écran dès que celui-ci change de couleur.
              </label><br>
              <label>
                <input type="radio" name="q1" value="C">
                Dès que tu auras appuyé sur 'Commencer', prépare-toi à appuyer sur l'écran dès que celui-ci change de couleur.
              </label><br>
              <label>
                <input type="radio" name="q1" value="D">
                Dès que tu auras appuyé sur 'Commencer', prépare-toi à cliquer sur l'écran dès que celui-ci change de teinte.
              </label>
            </div>
          </div>
  
          <div class="question">
            <p><strong>2. Que conseillent précisément les règles pour indiquer ta rapidité ?</strong></p>
            <div class="options" style="margin-left:20px;">
              <label>
                <input type="radio" name="q2" value="A">
                Sois réactif, ton temps sera mesuré très précisemment !
              </label><br>
              <label>
                <input type="radio" name="q2" value="B">
                Sois réactif, ton temps sera mesuré avec précision !
              </label><br>
              <label>
                <input type="radio" name="q2" value="C">
                Sois attentif, ton temps sera mesuré très précisemment !
              </label><br>
              <label>
                <input type="radio" name="q2" value="D">
                Sois attentif, ton score sera mesuré avec précision !
              </label>
            </div>
          </div>
  
          <div class="question">
            <p><strong>3. Quel est le signal visuel exact à ne surtout pas rater ?</strong></p>
            <div class="options" style="margin-left:20px;">
              <label>
                <input type="radio" name="q3" value="A">
                Il faut cliquer dès que ce dernier change sa couleur.
              </label><br>
              <label>
                <input type="radio" name="q3" value="B">
                Il faut cliquer dès que celui-ci change de couleur.
              </label><br>
              <label>
                <input type="radio" name="q3" value="C">
                Il faut appuyer dès que ce dernier change de couleur.
              </label><br>
              <label>
                <input type="radio" name="q3" value="D">
                Il faut appuyer dès que celui-ci change de nuance.
              </label>
            </div>
          </div>
  
          <div class="question">
            <p><strong>4. Après avoir cliqué sur 'Commencer', que dois-tu exactement faire ?</strong></p>
            <div class="options" style="margin-left:20px;">
              <label>
                <input type="radio" name="q4" value="A">
                Prépare-toi à cliquer sur l'écran.
              </label><br>
              <label>
                <input type="radio" name="q4" value="B">
                Tiens-toi prêt à cliquer sur l'écran.
              </label><br>
              <label>
                <input type="radio" name="q4" value="C">
                Prépare-toi à appuyer sur l'écran.
              </label><br>
              <label>
                <input type="radio" name="q4" value="D">
                Tiens-toi prêt à appuyer sur l'écran.
              </label>
            </div>
          </div>
  
          <div class="question">
            <p><strong>5. Quel conseil est donné concernant ton attitude globale pendant la partie ?</strong></p>
            <div class="options" style="margin-left:20px;">
              <label>
                <input type="radio" name="q5" value="A">
                sois attentif.
              </label><br>
              <label>
                <input type="radio" name="q5" value="B">
                Sois rapide.
              </label><br>
              <label>
                <input type="radio" name="q5" value="C">
                Sois très rapide.
              </label><br>
              <label>
                <input type="radio" name="q5" value="D">
                Sois réactif.
              </label>
            </div>
          </div>
  
          <!-- Bouton interne pour valider les réponses -->
          <button id="verifierReponses">Valider les réponses</button>
  
          <!-- Zone d'affichage du résultat -->
          <div class="result" id="resultat"></div>
        `;
    }
  
    /**
     * Fonction qui vérifie les réponses sélectionnées et affiche le score.
     */
    function verifierReponses() {
    let score = 0;
    const totalQuestions = 5;

    // Réponses correctes EXACTES (issues des règles)
    // Q1 = B
    // Q2 = A (avec "très précisemment" et "Sois réactif, ton temps sera mesuré")
    // Q3 = B
    // Q4 = A
    // Q5 = A

    const reponse1 = document.querySelector('input[name="q1"]:checked');
    if (reponse1 && reponse1.value === "B") score++;

    const reponse2 = document.querySelector('input[name="q2"]:checked');
    if (reponse2 && reponse2.value === "A") score++;

    const reponse3 = document.querySelector('input[name="q3"]:checked');
    if (reponse3 && reponse3.value === "B") score++;

    const reponse4 = document.querySelector('input[name="q4"]:checked');
    if (reponse4 && reponse4.value === "A") score++;

    const reponse5 = document.querySelector('input[name="q5"]:checked');
    if (reponse5 && reponse5.value === "D") score++;

    const resultat = document.getElementById('resultat');
    if (score === totalQuestions) {
        resultat.innerHTML = "✔️ Parfait ! Vous avez choisi toutes les formulations EXACTES. Le jeu va démarrer.";
        resultat.style.color = "green";
        resultat.style.fontWeight = "bold";
        resultat.style.textShadow = "1px 1px 1px black";
        sleep(5000).then(() => {
        
        game_begin = true;
        debut_jeu();
        });
    } else {
        resultat.innerHTML = "❌ Vous avez " + score + "/" + totalQuestions
                            + ". Réessayez en repérant les subtilités de vocabulaire.";
        resultat.style.color = "red";
        resultat.style.fontWeight = "bold";
        resultat.style.textShadow = "1px 1px 1px black";
    }
    }
            
        
});