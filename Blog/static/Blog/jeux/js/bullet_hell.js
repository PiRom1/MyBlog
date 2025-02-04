document.addEventListener('DOMContentLoaded', function () {
  const startButton = document.getElementById('startButton');
  // Ajout récupération du CSRF token
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  startButton.addEventListener('click', function () {
    // Start the game
    document.body.innerHTML = '<canvas id="gameCanvas"></canvas><div id="score"></div>';
    document.body.style.background = 'black';
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    // Ajustement de la taille du canvas à la fenêtre
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    window.addEventListener("resize", () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    });

    // Définition du joueur
    const player = {
      x: canvas.width / 2,
      y: canvas.height / 2,
      radius: 5,
      speed: 5
    };

    // Gestion des touches pour le déplacement
    const keys = {
      ArrowUp: false,
      ArrowDown: false,
      ArrowLeft: false,
      ArrowRight: false
    };

    window.addEventListener("keydown", (e) => {
      if (e.key in keys) keys[e.key] = true;
    });
    window.addEventListener("keyup", (e) => {
      if (e.key in keys) keys[e.key] = false;
    });

    // Tableau des projectiles
    const bullets = [];

    // Classe Bullet pour gérer les projectiles
    class Bullet {
      constructor(x, y, dx, dy, radius = 3, color = "red") {
        this.x = x;
        this.y = y;
        this.dx = dx;
        this.dy = dy;
        this.radius = radius;
        this.color = color;
      }
      update() {
        this.x += this.dx;
        this.y += this.dy;
      }
      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.fill();
      }
    }

    // Variables pour le score et la gestion du temps
    let startTime = Date.now();
    let gameOver = false;
    let spawnInterval = 1000; // Intervalle initial entre spawns (en ms)
    let lastSpawnTime = 0;

    // Fonction pour faire apparaître un projectile
    function spawnBullet() {
      // Le projectile apparaît aléatoirement sur l’un des bords de l’écran
      let edge = Math.floor(Math.random() * 4);
      let x, y;
      switch (edge) {
        case 0: // Haut
          x = Math.random() * canvas.width;
          y = 0;
          break;
        case 1: // Droit
          x = canvas.width;
          y = Math.random() * canvas.height;
          break;
        case 2: // Bas
          x = Math.random() * canvas.width;
          y = canvas.height;
          break;
        case 3: // Gauche
          x = 0;
          y = Math.random() * canvas.height;
          break;
      }
      // Calcul de l’angle pour que le projectile se dirige vers le joueur
      let angle = Math.atan2(player.y - y, player.x - x);
      
      // Décider du type de projectile: 10% bleu, 10% vert, sinon rouge.
      let rand = Math.random();
      let bulletRadius, baseSpeed, color;
      if (rand < 0.05) {
          // Bullet bleu
          bulletRadius = 10;
          baseSpeed = 1.3;
          color = "blue";
      } else if (rand < 0.15) {
          // Bullet vert (plus petit et très rapide)
          bulletRadius = 2;
          baseSpeed = 5;
          color = "lime";
      } else {
          // Bullet rouge
          bulletRadius = 3;
          baseSpeed = 2;
          color = "red";
      }
      
      const speed = baseSpeed + (color === "blue" ? Math.random() * 0.5 : Math.random());
      const dx = Math.cos(angle) * speed;
      const dy = Math.sin(angle) * speed;
      bullets.push(new Bullet(x, y, dx, dy, bulletRadius, color));
    }

    // Détection de collision entre le joueur et un projectile
    function isColliding(bullet) {
      const dx = bullet.x - player.x;
      const dy = bullet.y - player.y;
      const distance = Math.hypot(dx, dy);
      return distance < bullet.radius + player.radius;
    }

    // Boucle principale du jeu
    function update() {
      if (gameOver) return;

      // Effacer le canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Calcul et affichage du score (temps de survie en secondes)
      const currentTime = Date.now();
      const score = ((currentTime - startTime) / 1000).toFixed(2);
      document.getElementById("score").textContent = "Score: " + score;

      // Mise à jour du déplacement du joueur
      if (keys.ArrowUp && player.y - player.radius > 0) player.y -= player.speed;
      if (keys.ArrowDown && player.y + player.radius < canvas.height) player.y += player.speed;
      if (keys.ArrowLeft && player.x - player.radius > 0) player.x -= player.speed;
      if (keys.ArrowRight && player.x + player.radius < canvas.width) player.x += player.speed;

      // Dessiner le joueur
      ctx.beginPath();
      ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
      ctx.fillStyle = "white";
      ctx.fill();

      // Mise à jour et dessin des projectiles
      for (let i = bullets.length - 1; i >= 0; i--) {
        const bullet = bullets[i];
        bullet.update();
        bullet.draw();

        // Collision avec le joueur
        if (isColliding(bullet)) {
          gameOver = true;
          // Enregistrement du score
          fetch('/jeux/record', {
            method: 'POST',
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({ game: 'Bullet_Hell', score: score })
          })
          .then(response => response.json())
          .then(data => console.log("Score registered!"));
          
          // Création de l'écran de Game Over inspiré de draw_end de kingboard
          document.body.innerHTML = '';
          document.body.style.background = 'red';
          
          const title = document.createElement('h1');
          title.textContent = 'Game Over';
          document.body.appendChild(title);
          
          const scorePara = document.createElement('p');
          scorePara.textContent = `Score: ${score}`;
          document.body.appendChild(scorePara);
          
          const messagePara = document.createElement('p');
          messagePara.textContent = "Seulement ça? tu appuies sur les fleches avec le front ou quoi pour être si lent?";
          document.body.appendChild(messagePara);
          
          const replay = document.createElement('button');
          replay.textContent = "Rejouer !";
          replay.style.fontSize = "20px";
          replay.style.padding = "10px 20px";
          replay.style.marginTop = "20px";
          replay.addEventListener("click", function() {
              location.reload();
          });
          document.body.appendChild(replay);
          
          const link = document.createElement('a');
          link.href = '/jeux';
          link.textContent = "Retour à la liste de jeux.";
          link.style.position = 'absolute';
          link.style.left = '5px';
          link.style.top = '10px';
          document.body.appendChild(link);
          
          return;
        }

        // Suppression des projectiles hors écran pour optimiser
        if (
          bullet.x < -10 || bullet.x > canvas.width + 10 ||
          bullet.y < -10 || bullet.y > canvas.height + 10
        ) {
          bullets.splice(i, 1);
        }
      }

      // Apparition de nouveaux projectiles avec une fréquence croissante
      const timeSinceLastSpawn = currentTime - lastSpawnTime;
      if (timeSinceLastSpawn > spawnInterval) {
        let bulletsToSpawn = 5 + Math.floor(score); // Nombre de projectiles à faire apparaître
        for (let i = 0; i < bulletsToSpawn; i++) {
          spawnBullet();
        }
        lastSpawnTime = currentTime;
        // Diminution progressive de l'intervalle entre les spawns, avec une limite minimale
        spawnInterval = Math.max(500, spawnInterval - 10);
      }

      requestAnimationFrame(update);
    }

    update();
  });
});
