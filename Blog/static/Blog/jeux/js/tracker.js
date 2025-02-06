document.addEventListener('DOMContentLoaded', async function () {
    // Récupérer le CSRF token depuis le meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    async function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    const bouton = document.getElementById('bouton');

    
    let screenDiagonal = Math.min(window.innerWidth, window.innerHeight);
    console.log("screen : ", screenDiagonal);
    let canvas;
    let ctx;
    const CIRCLE_COLOR = 'red';
    let CIRCLE_RADIUS = screenDiagonal * 0.04;

    let CIRCLE_X = window.innerWidth/2;
    let CIRCLE_Y = window.innerHeight/2;

    let mouse_x;
    let mouse_y;

    let ANGLE_MOUVEMENT = randint(-Math.PI, Math.PI);
    let COEFF_MOUVEMENT = 0.00045 * screenDiagonal;

    let begin, end;

    document.addEventListener('mousemove', function(event) {
        mouse_x = event.clientX;
        mouse_y = event.clientY;
    });



    bouton.addEventListener('click', function(e) {
        debut_jeu();
    })

    function randint(min, max) {
        return min + Math.random() * (max - min);
    }



    function draw_circle() {
        
        ctx.clearRect(0,0,canvas.width,canvas.height);
        ctx.beginPath();
        ctx.arc(CIRCLE_X, CIRCLE_Y, CIRCLE_RADIUS, 0, Math.PI * 2);
        ctx.fillStyle = CIRCLE_COLOR;
        ctx.fill();
        ctx.closePath();
        };
    
    function move_circle() {
        let angle_x = Math.cos(ANGLE_MOUVEMENT);
        let angle_y = Math.sin(ANGLE_MOUVEMENT);
        CIRCLE_X += angle_x * COEFF_MOUVEMENT;
        CIRCLE_Y += angle_y * COEFF_MOUVEMENT;
        ANGLE_MOUVEMENT += randint(-2, 2) / 10;

        if (CIRCLE_X <= CIRCLE_RADIUS) {
            ANGLE_MOUVEMENT += Math.PI/2;
            CIRCLE_X = CIRCLE_RADIUS;
        }
        if (CIRCLE_X >= canvas.width - CIRCLE_RADIUS) {
            ANGLE_MOUVEMENT += Math.PI/2;
            CIRCLE_X = canvas.width - CIRCLE_RADIUS;
        }
        if (CIRCLE_Y <= CIRCLE_RADIUS) {
            ANGLE_MOUVEMENT += Math.PI/2;
            CIRCLE_Y = CIRCLE_RADIUS;
        }
        if (CIRCLE_Y >= canvas.height - CIRCLE_RADIUS) {
            ANGLE_MOUVEMENT += Math.PI/2;
            CIRCLE_Y = canvas.height - CIRCLE_RADIUS;
        } 

    }

    function draw_end() {
        const time = (end - begin) / 1000;
        document.body.innerHTML = '<h1>CONCENTRE TOI 2 MINUTES NON ???</h1>';
        let h2 = document.createElement('h2');
        h2.innerHTML = `<h2>Tu n'as tenu que ${time} secondes ... </h2>`;
        document.body.appendChild(h2);
        document.body.style.backgroundImage = 'url()';
        document.body.style.backgroundColor = 'red';


        const replay = document.createElement("button");
        replay.style.display = "block";
        replay.style.margin = "0 auto";
        replay.style.textAlign = "center";
        replay.textContent = "Rejouer !";

        // Modification: Restart the game without reloading the page.
        replay.addEventListener("click", function() {
            document.body.innerHTML = ''; // Clear previous game elements.
            debut_jeu(); // Restart the game.
        });

        document.body.appendChild(replay);

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
            body: JSON.stringify({game: 'tracker', score: time})  // Envoie des données dans le corps de la requête
            })        
        .then(response => response.json())
        .then(data => {
            console.log("Donnée bien enregistrée !");
            })
}
    
    function distance(x1, y1, x2, y2) {
        const dx = x1 - x2;
        const dy = y1 - y2;

        return Math.sqrt(dx*dx + dy*dy)
    }

    async function draw_decompte() {
        let h1 = document.createElement('h1');
        h1.style.position = 'absolute';
        h1.style.top = '10%';
        h1.style.left = '50%';
        h1.innerHTML = '<h1>2 ...</h1>';
        document.body.appendChild(h1);
        await sleep(1000);
        h1.innerHTML = '<h1>1 ...</h1>';
        await sleep(1000);
        h1.innerHTML = '';
    }
    
    

    async function debut_jeu() {
        document.body.innerHTML = '';
        document.body.style.background = 'black';
        
        // Reset circle position, size and movement speed
        CIRCLE_X = window.innerWidth / 2;
        CIRCLE_Y = window.innerHeight / 2;
        screenDiagonal = Math.min(window.innerWidth, window.innerHeight);
        CIRCLE_RADIUS = screenDiagonal * 0.04;
        COEFF_MOUVEMENT = 0.00045 * screenDiagonal;
        
        // Afficher le rond
        canvas = document.createElement('canvas');
        ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        document.body.appendChild(canvas);
        draw_circle(canvas, [CIRCLE_X, CIRCLE_Y]);

        await draw_decompte();

        begin = Date.now();
        let timer = setInterval(() => {
            
            if (distance(mouse_x, mouse_y, CIRCLE_X, CIRCLE_Y) >= CIRCLE_RADIUS) {
                // Stoppe le timer lorsqu'il atteint 0
                end = Date.now();
                clearInterval(timer); 
                draw_end();
            }
            draw_circle(canvas, CIRCLE_X, CIRCLE_Y)
            move_circle();
            console.log(CIRCLE_X, CIRCLE_Y);
            COEFF_MOUVEMENT += 0.002;
            if (CIRCLE_RADIUS >= 10) {
                CIRCLE_RADIUS -= 0.01;
            }
            
            
          }, 10);


        

    }

});