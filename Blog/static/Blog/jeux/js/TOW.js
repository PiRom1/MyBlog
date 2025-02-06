// static/Blog/jeux/js/TOW.js
document.addEventListener('DOMContentLoaded', function() {
    // État initial du jeu
    let score = 0;
    const threshold = 5;  // Seuil de victoire (score = +5 ou -5)
    
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const resultP = document.getElementById('result');

    // Positions de référence pour le dessin
    const leftEndpoint = 50;           // Position x du joueur de gauche
    const rightEndpoint = 550;         // Position x du joueur de droite
    const ropeY = canvas.height / 2;     // Hauteur de la corde (au milieu du canvas)
    const centerX = canvas.width / 2;    // Centre géométrique du canvas
    const halfRopeLength = (rightEndpoint - leftEndpoint) / 2;  // Pour calculer le décalage

    /**
     * Dessine le jeu dans le canvas :
     * - La corde (trait blanc)
     * - Le triangle rouge indiquant le centre de la corde (déplacé selon le score)
     * - Les deux joueurs aux extrémités (cercles)
     */
    function drawGame() {
        // Efface le canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Dessiner la corde (trait blanc)
        ctx.beginPath();
        ctx.moveTo(leftEndpoint, ropeY);
        ctx.lineTo(rightEndpoint, ropeY);
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 4;
        ctx.stroke();

        // Calcul de la position du centre de la corde en fonction du score.
        // Pour score = threshold, le centre est à droite (x = rightEndpoint),
        // pour score = -threshold, il est à gauche (x = leftEndpoint).
        let offset = (score / threshold) * halfRopeLength;
        let triangleX = centerX + offset;

        // Dessiner le triangle rouge (indiquant le centre actuel de la corde)
        // On le dessine sous forme d'un triangle pointant vers le haut.
        ctx.beginPath();
        ctx.moveTo(triangleX, ropeY - 15);      // Pointe supérieure
        ctx.lineTo(triangleX - 10, ropeY + 10);   // Coin inférieur gauche
        ctx.lineTo(triangleX + 10, ropeY + 10);   // Coin inférieur droit
        ctx.closePath();
        ctx.fillStyle = 'red';
        ctx.fill();

        // Dessiner le Joueur 1 (à gauche) : un cercle bleu
        ctx.beginPath();
        ctx.arc(leftEndpoint, ropeY, 15, 0, 2 * Math.PI);
        ctx.fillStyle = 'blue';
        ctx.fill();

        // Dessiner le Joueur 2 (à droite) : un cercle vert
        ctx.beginPath();
        ctx.arc(rightEndpoint, ropeY, 15, 0, 2 * Math.PI);
        ctx.fillStyle = 'green';
        ctx.fill();
    }

    // Premier dessin
    drawGame();

    // Établir la connexion WebSocket
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const gameSocket = new WebSocket(ws_scheme + '://' + window.location.host + '/ws/tiracorde/');

    gameSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        // On s'attend à recevoir des messages contenant "score", "last_player" et éventuellement "winner"
        if (data.score !== undefined) {
            score = data.score;
            drawGame();
            if (data.winner) {
                resultP.textContent = "Le gagnant est : " + data.winner;
            } else if (data.last_player) {
                resultP.textContent = data.last_player + " a tiré !";
            }
        }
    };

    gameSocket.onclose = function(e) {
        console.error('La connexion WebSocket a été fermée.');
    };

    // Gérer le clic sur le bouton du Joueur 1
    document.getElementById('player1-btn').addEventListener('click', function() {
        gameSocket.send(JSON.stringify({
            'action': 'pull',
            'player': 'player1'
        }));
    });

    // Gérer le clic sur le bouton du Joueur 2
    document.getElementById('player2-btn').addEventListener('click', function() {
        gameSocket.send(JSON.stringify({
            'action': 'pull',
            'player': 'player2'
        }));
    });
});
