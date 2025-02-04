document.addEventListener('DOMContentLoaded', function () {
  const startButton = document.getElementById('startButton');
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  
  // New function to encapsulate the game logic and initialization
  function startGame() {
    // Set up the game DOM and styling
    document.body.innerHTML = '<canvas id="gameCanvas"></canvas><div id="score"></div>';
    document.body.style.margin = '0'; // Remove default margin
    
    const canvas = document.getElementById("gameCanvas");
    canvas.style.backgroundColor = "black"; // Canvas background remains black
    const ctx = canvas.getContext("2d");
    
    // Définir la résolution virtuelle fixe
    const GAME_WIDTH = 1536;
    const GAME_HEIGHT = 695;
    
    // La logique du jeu se base sur ces dimensions fixes
    canvas.width = GAME_WIDTH;
    canvas.height = GAME_HEIGHT;
    
    // On utilise le CSS pour que le canvas occupe toute la fenêtre,
    // en adaptant l’affichage, mais pas la logique
    function resizeCanvasDisplay() {
      // On calcule un ratio pour que le canvas garde son ratio sans déformation
      const ratio = Math.min(window.innerWidth / GAME_WIDTH, window.innerHeight / GAME_HEIGHT);
      canvas.style.width = (GAME_WIDTH * ratio) + 'px';
      canvas.style.height = (GAME_HEIGHT * ratio) + 'px';
    }
    resizeCanvasDisplay();
    window.addEventListener("resize", resizeCanvasDisplay);
    
    // --- Début de votre logique de jeu ---
    
    // Définition du joueur dans l'espace virtuel
    const player = {
      x: GAME_WIDTH / 2,
      y: GAME_HEIGHT / 2,
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
    
    // Mise à jour de la gestion des touches pour inclure z,q,s,d
    window.addEventListener("keydown", (e) => {
      let key = e.key;
      if (key === "z") key = "ArrowUp";
      if (key === "q") key = "ArrowLeft";
      if (key === "s") key = "ArrowDown";
      if (key === "d") key = "ArrowRight";
      if (key in keys) keys[key] = true;
    });
    window.addEventListener("keyup", (e) => {
      let key = e.key;
      if (key === "z") key = "ArrowUp";
      if (key === "q") key = "ArrowLeft";
      if (key === "s") key = "ArrowDown";
      if (key === "d") key = "ArrowRight";
      if (key in keys) keys[key] = false;
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
    
    let startTime = Date.now();
    let gameOver = false;
    let spawnInterval = 1000;
    let lastSpawnTime = 0;
    
    function spawnBullet() {
      let edge = Math.floor(Math.random() * 4);
      let x, y;
      switch (edge) {
        case 0: // Haut
          x = Math.random() * GAME_WIDTH;
          y = 0;
          break;
        case 1: // Droit
          x = GAME_WIDTH;
          y = Math.random() * GAME_HEIGHT;
          break;
        case 2: // Bas
          x = Math.random() * GAME_WIDTH;
          y = GAME_HEIGHT;
          break;
        case 3: // Gauche
          x = 0;
          y = Math.random() * GAME_HEIGHT;
          break;
      }
      let angle = Math.atan2(player.y - y, player.x - x);
      
      // Choix du type de projectile
      let rand = Math.random();
      let bulletRadius, baseSpeed, color;
      if (rand < 0.05) {
          bulletRadius = 15;
          baseSpeed = 1.3;
          color = "blue";
      } else if (rand < 0.15) {
          bulletRadius = 2;
          baseSpeed = 5;
          color = "lime";
      } else {
          bulletRadius = 3;
          baseSpeed = 2;
          color = "red";
      }
      const speed = baseSpeed * 1.4;
      const dx = Math.cos(angle) * speed;
      const dy = Math.sin(angle) * speed;
      bullets.push(new Bullet(x, y, dx, dy, bulletRadius, color));
    }
    
    function isColliding(bullet) {
      const dx = bullet.x - player.x;
      const dy = bullet.y - player.y;
      const distance = Math.hypot(dx, dy);
      return distance < bullet.radius + player.radius;
    }
    
    function update() {
      if (gameOver) return;
      
      // Effacer le canvas (dans l'espace de jeu virtuel)
      ctx.clearRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
      const currentTime = Date.now();
      const score = ((currentTime - startTime) / 1000).toFixed(2);
      document.getElementById("score").textContent = "Score: " + score;
      
      // Déplacement du joueur (toujours dans l'espace 800×600)
      if (keys.ArrowUp && player.y - player.radius > 0) player.y -= player.speed;
      if (keys.ArrowDown && player.y + player.radius < GAME_HEIGHT) player.y += player.speed;
      if (keys.ArrowLeft && player.x - player.radius > 0) player.x -= player.speed;
      if (keys.ArrowRight && player.x + player.radius < GAME_WIDTH) player.x += player.speed;
      
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
          
          // Écran de Game Over
          document.body.innerHTML = '';
          document.body.style.background = 'red';
          const title = document.createElement('h1');
          title.textContent = 'Game Over';
          document.body.appendChild(title);
          const scorePara = document.createElement('p');
          scorePara.textContent = `Score: ${score}`;
          document.body.appendChild(scorePara);
          const messagePara = document.createElement('p');
          messagePara.textContent = "Seulement ça? Tu appuies sur les flèches avec le front ou quoi pour être si lent?";
          document.body.appendChild(messagePara);
          const replay = document.createElement('button');
          replay.textContent = "Rejouer !";
          replay.style.fontSize = "20px";
          replay.style.padding = "10px 20px";
          replay.style.marginTop = "20px";
          replay.addEventListener("click", function() {
              // Restart the game instead of reloading the page
              startGame();
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
        
        // Suppression des projectiles hors du monde de jeu
        if (
          bullet.x < -10 || bullet.x > GAME_WIDTH + 10 ||
          bullet.y < -10 || bullet.y > GAME_HEIGHT + 10
        ) {
          bullets.splice(i, 1);
        }
      }
      
      // Apparition de nouveaux projectiles
      const timeSinceLastSpawn = currentTime - lastSpawnTime;
      if (timeSinceLastSpawn > spawnInterval) {
        let bulletsToSpawn = 5 + Math.floor(score);
        for (let i = 0; i < bulletsToSpawn; i++) {
          spawnBullet();
        }
        lastSpawnTime = currentTime;
        spawnInterval = Math.max(500, spawnInterval - 10);
      }
      
      requestAnimationFrame(update);
    }
    
    update();
  }
  
  // Change the start button to launch the game via startGame
  startButton.addEventListener('click', function () {
    startGame();
  });
});
