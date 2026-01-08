document.addEventListener('DOMContentLoaded', async function () {
    // Récupérer le CSRF token depuis le meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    async function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    const bouton = document.getElementById('bouton');

    // General
    let screenDiagonal = Math.min(window.innerWidth, window.innerHeight);
    let canvas;
    let ctx;
    let mouse_x;
    let mouse_y;

    let GRAVITY = 0.981;
    let COEFF_REBOND = 0.65;
    let FROTTEMENTS_HORIZONTAUX = 0.99;
    let nb_paniers = 0;
    let MAX_TIME = 10; // Temps en secondes
    let MAX_WIDTH = 1/2 * window.innerWidth;

    let LEFT_TERRAIN_COLOR = "#445B52"
    let RIGHT_TERRAIN_COLOR = "#3A4654";

    // Ball
    let BALL_X = 3/5 * window.innerWidth;
    let BALL_Y = 3/5 * window.innerHeight;
    let BALL_COLOR = '#F7C59F'
    let BALL_RADIUS = screenDiagonal * 0.015;

    // Player
    let PLAYER_WIDTH = screenDiagonal * 0.1;
    let PLAYER_HEIGHT = screenDiagonal * 0.1;
    let TOSS_COLOR = '#8EC5D6';
    let CATCH_COLOR = '#F4A7B9';
    let player_state = 'toss';
    let FORCE_TRANSMISSION = 0.85;

    // Basket
    let BASKET_WIDTH = 50;
    let BASKET_HEIGHT = 10;
    let BASKET_COLOR = '#E07A5F'
    let basket;
    let BASKET_BORDER_WIDTH = 8;
    let BASKET_BORDER_COLOR = "#fedecc";

    // Text
    let text_paniers = document.createElement('p');
    text_paniers.classList = 'text-paniers';

    let text_timer = document.createElement('p');
    text_timer.classList = 'text-timer';

    
    function draw_terrain() {
        // LEFT TERRAIN
        ctx.beginPath();
        ctx.rect(0, 0, MAX_WIDTH, window.innerHeight);
        ctx.fillStyle = LEFT_TERRAIN_COLOR;
        ctx.fill();

        // RIGHT TERRAIN
        ctx.beginPath();
        ctx.rect(MAX_WIDTH, 0, window.innerWidth - MAX_WIDTH, window.innerHeight);
        ctx.fillStyle = RIGHT_TERRAIN_COLOR;
        ctx.fill();

    }


    function distance(x1, y1, x2, y2) {
        const dx = x1 - x2;
        const dy = y1 - y2;

        return Math.sqrt(dx*dx + dy*dy)
    }

    // Classes

    class Basket {
        constructor(x, y, width, height, color, border_width, border_color) {
            this.x = x;
            this.y = y;
            this.color = color;
            this.width = width;
            this.border_width = border_width;
            this.border_color = border_color
            this.height = height;
        }

        draw() {
            ctx.beginPath();
            ctx.rect(this.x - this.width/2 - this.border_width, this.y - this.height/2, this.width + 2*this.border_width, this.height);
            ctx.fillStyle = this.border_color;
            ctx.fill();

            ctx.beginPath();
            ctx.rect(this.x - this.width/2, this.y - this.height/2, this.width, this.height);
            ctx.fillStyle = this.color;
            ctx.fill();
        }

        collisions(ball) { // Manage collisions between the ball and the basket

            if (ball.x > this.x - this.width/2 - ball.radius - this.border_width) {
                if (ball.x < this.x - this.width/2 - ball.radius) { 
                    if (ball.y > this.y - this.height/2 - ball.radius) {
                        if (ball.y < this.y + this.height/2 + ball.radius) { // Collision border gauche
                            ball.dy = -ball.dy
                        }
                    }
                }
            }

            if (ball.x > this.x + this.width/2 + ball.radius) {
                if (ball.x < this.x + this.width/2 + ball.radius + this.border_width) { 
                    if (ball.y > this.y - this.height/2 - ball.radius) {
                        if (ball.y < this.y + this.height/2 + ball.radius) { // Collision border gauche
                            ball.dy = -ball.dy
                        }
                    }
                }
            }



           
            if (ball.x > this.x - this.width/2 - ball.radius) {
                if (ball.x < this.x + this.width/2 + ball.radius) { // Si x collides
                    if (ball.y > this.y - this.height/2 - ball.radius) {
                        if (ball.y < this.y + this.height/2 + ball.radius) { // Si y collides
                            console.log("collision");
                            if (ball.y > this.y) { // Collision par le bas
                                ball.dy = 0;
                            }
                            else { // Collision par le haut
                                nb_paniers += 1;
                                text_paniers.innerHTML = `Points : ${nb_paniers}`;
                                basket = generate_random_basket();
                            }

                        }
                    }
                }
            }

        }

    }

    function generate_random_basket() {
        return new Basket(
            randint(BASKET_WIDTH + BASKET_BORDER_WIDTH, MAX_WIDTH - BASKET_WIDTH - BASKET_BORDER_WIDTH),                            // X
            randint(1/5 * window.innerHeight + BASKET_HEIGHT, window.innerHeight / 2),  // Y
            BASKET_WIDTH,                                                               // Width
            BASKET_HEIGHT,                                                              // Height
            BASKET_COLOR,                                                               // COLOR
            BASKET_BORDER_WIDTH,                                                        // BORDER WIDTH
            BASKET_BORDER_COLOR                                                         // BORDER_COLOR
        );
    }






    class Ball {
      constructor(x, y, radius, color) {
        this.x = x;
        this.y = y;
        this.dx = 0;
        this.dy = 0;
        this.radius = radius;
        this.color = color;
        this.caught = false;

        this.offset_x = 0;
        this.offset_y = 0;
      }

      move(main = null) {

        if (this.caught && main) {
            this.x = main.x + this.offset_x;
            this.y = main.y + this.offset_y;
            return
        }

        this.gravity()
        this.dx = this.dx * FROTTEMENTS_HORIZONTAUX;
        this.x += this.dx
        this.y += this.dy
        
        if (this.x < this.radius){
            this.x = this.radius
            this.dx = -this.dx
        }
        if (this.x > window.innerWidth - this.radius) {
            this.x = window.innerWidth - this.radius
            this.dx = -this.dx
        }
        
        if (this.y < this.radius) {
            this.y = this.radius
            this.dy = 0
        }
        if (this.y > window.innerHeight - this.radius) {
            this.y = window.innerHeight - this.radius
            this.dy = -this.dy * COEFF_REBOND
        }

        if (this.y >= window.innerHeight - this.radius) {
            if (this.x < MAX_WIDTH + this.radius) {
                this.dx += 0.1;
            }
        }



      }

      gravity() {
        this.dy += GRAVITY;
      }

      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.fill();
      }
    
    }


    class Player {
        constructor(size) {
            this.size = size;
            this.x = 10;
            this.y = 10;
            this.toss_color = TOSS_COLOR;
            this.catch_color = CATCH_COLOR;
            this.state = 'toss';

            this.dx = 0;
            this.dy = 0;
        }

        get_pos(pos) {        
            
            
            if (pos[0] < MAX_WIDTH + this.size/2) {
                pos[0] = MAX_WIDTH + this.size/2;
            }
            else if (pos[0] > window.innerWidth - this.size/2) {
                pos[0] = window.innerWidth - this.size/2;
            }
            
            if (pos[1] < this.size/2) {
                pos[1] = this.size/2;
            }
            else if (pos[1] > window.innerHeight - this.size/2) {
                pos[1] = window.innerHeight - this.size/2;
            }

            this.dx = pos[0] - this.x;
            this.dy = pos[1] - this.y;

            this.x = pos[0];
            this.y = pos[1];
            

            
        }
    
        draw() {
            ctx.beginPath();
            ctx.rect(this.x - this.size/2, this.y - this.size/2, this.size, this.size);
            let color;
            if (this.state === 'toss') {
                color = this.toss_color;
            }
            else {
                color = this.catch_color;
            }
            ctx.fillStyle = color;
            ctx.fill();
        }
    
    
        grab(ball) {
            
            // if (distance(this.x, this.y, ball.x, ball.y) < Math.max(this.size/2, ball.radius)) { // On attrape la balle
            if (this.x > ball.x - ball.radius - this.size/2) {
                if (this.x < ball.x + ball.radius + this.size/2) {
                    if (this.y > ball.y - ball.radius - this.size/2) {
                        if (this.y < ball.y + ball.radius + this.size/2) {                    
                            ball.dx = 0
                            ball.dy = 0
                            ball.caught = true
                            ball.offset_x = ball.x - this.x
                            ball.offset_y = ball.y - this.y
                            console.log("balle attrapée")
                        }
                    }
                }
            }
            else {
                ball.caught = false
            }
            
        }

    }
                
                






    document.addEventListener('mousemove', function(event) {
        mouse_x = event.clientX;
        mouse_y = event.clientY;
    });

    document.addEventListener('mousedown', function() {
        player_state = 'catch';
    })
    document.addEventListener('mouseup', function() {
        player_state = 'toss';
    })



    bouton.addEventListener('click', function(e) {
        debut_jeu();
    })

    function randint(min, max) {
        return min + Math.random() * (max - min);
    }



    function draw_end() {

        document.body.innerHTML = `<h1>C'est ... NAVRANT !</h1>`;
        let h2 = document.createElement('h2');
        h2.innerHTML = `<h2>Tu n'as marqué que ${nb_paniers} paniers ... </h2>`;
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
            body: JSON.stringify({game: 'basket', score: nb_paniers})  // Envoie des données dans le corps de la requête
            })        
        .then(response => response.json())
        .then(data => {
            console.log("Donnée bien enregistrée !");
            })
}
    
    
    

    function debut_jeu() {

        nb_paniers = 0;
        document.body.innerHTML = '';
        document.body.style.background = 'black';

        document.body.appendChild(text_paniers);
        text_paniers.innerHTML = "Points : 0";

        document.body.appendChild(text_timer);
        text_timer.innerHTML = "Temps : 10s";
        
        
        // Reset circle position, size and movement speed
        let player = new Player(PLAYER_WIDTH, PLAYER_HEIGHT);
        let ball = new Ball(BALL_X, BALL_Y, BALL_RADIUS, BALL_COLOR);
        basket = generate_random_basket();
       

        canvas = document.createElement('canvas');
        ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        document.body.appendChild(canvas);
        
        let ms = 10;
        let nb_iter = (1000 * MAX_TIME) / ms
        let n = 0;

        let timer = setInterval(() => {
            
            if (n >= nb_iter) {
                // Stoppe le timer lorsqu'il atteint 0
                if (ball.caught === false && ball.y < window.innerHeight - ball.radius) {
                    n = nb_iter;
                } // Si la balle est en l'air et non tenue, on attend
                else {
                    clearInterval(timer); 
                    draw_end();
                }
            }
            

            text_timer.innerHTML = `Temps : ${Math.round( (MAX_TIME - (n * ms)/1000) * 100 ) / 100}`;

            
            ctx.clearRect(0,0,canvas.width,canvas.height);

            draw_terrain();

         

            basket.draw();

            player.get_pos([mouse_x, mouse_y]);
            
            player.state = player_state;
            player.draw();

            ball.move(player);
            basket.collisions(ball);

            ball.draw();

            if (player.state === 'catch') {
                player.grab(ball);
            }
            else {
                if (ball.caught) {
                    ball.dx = player.dx * FORCE_TRANSMISSION;
                    ball.dy = player.dy * FORCE_TRANSMISSION;
                    ball.caught = false;
                }
            }

            n += 1;
            
            
          }, ms);


        

    }

});