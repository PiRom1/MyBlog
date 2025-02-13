// Setup canvas and websocket connection
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');

let gameState = {
    ball: { x: 250, y: 150 },
    paddle1: { y: 100 },
    paddle2: { y: 100 }
};

// Retrieve room name from the DOM
const roomElem = document.querySelector('.game-container');
const roomName = roomElem ? roomElem.dataset.roomName : 'default';
// Update WebSocket connection URL to be relative:
const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
const ws = new WebSocket(`${ws_scheme}://${window.location.host}/ws/pong/${roomName}/`);

// Retrieve game data passed in the template via data attributes
const gameElem = document.querySelector('.game-data');
const gameData = gameElem ? {
    gameName: gameElem.dataset.gameName,
    gameSize: gameElem.dataset.gameSize,
    gameType: gameElem.dataset.gameType,
    player: gameElem.dataset.player,
    team: gameElem.dataset.team,
    role: gameElem.dataset.role
} : {};

ws.onopen = function() {
    console.log("Connected to game websocket for room:", roomName);
    // Send the init_lobby message once the websocket is open
    ws.send(JSON.stringify({
        type: 'init_lobby',
        game_name: gameData.gameName,
        game_size: gameData.gameSize,
        game_type: gameData.gameType,
        player: gameData.player,
        team: gameData.team,
        role: gameData.role
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if(data.type === 'game_update'){
        // update state from backend using new type
        gameState = { ...gameState, ...data.game_state };
        // update score display if available in gameState
        if(document.getElementById('score1') && document.getElementById('score2')) {
            document.getElementById('score1').textContent = gameState.score.team1;
            document.getElementById('score2').textContent = gameState.score.team2;
        }
    } else if(data.type === 'start_game'){
        // Initialize game state if required
        console.log("Game started", data.game_state);
        gameState = { ...gameState, ...data.game_state };
        if(document.getElementById('score1') && document.getElementById('score2')) {
            document.getElementById('score1').textContent = gameState.score.team1;
            document.getElementById('score2').textContent = gameState.score.team2;
        }
    } else if(data.type === 'all_players_connected'){
        // All players are connected; can display a message or unpause the game 
        console.log("All players connected: " + data.message);
        
        // Décompte de 3 secondes avant de démarrer le jeu
        let count = 3;
        const countdown = document.getElementById("countdown");
        countdown.textContent = "Le jeu va démarrer dans " + count;
        countdown.style.display = "block";

        const countdownPromise = new Promise((resolve) => {
            const countdownInterval = setInterval(() => {
            count--;
            countdown.textContent = "Le jeu va démarrer dans " + count;
            if (count <= 0) {
                clearInterval(countdownInterval);
                resolve();
            }
            }, 1000);
        });

        countdownPromise.then(() => {
            ws.send(JSON.stringify({ type: 'start_game'}));
        });
    } else if(data.type === 'verify'){
        // Optionally compare local and backend positions
        // ...existing verification logic...
    }
};

let keydown = false;

// Send key events to backend
document.addEventListener('keyup', (e) => {
    e.preventDefault();
    if (keydown && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
        ws.send(JSON.stringify({ type: 'key_input', data: {key: e.key, action: 'up' }}));
    }
    keydown = false;
});

document.addEventListener('keydown', (e) => {
    e.preventDefault();
    if (!keydown && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
        ws.send(JSON.stringify({ type: 'key_input', data: {key: e.key, action: 'down' }}));
        console.log("Keydown event sent");
    }
    keydown = true;
});

// Local animation loop for smooth drawing
function animate() {
    // ...existing code...
    ctx.clearRect(0,0, canvas.width, canvas.height);
    
    // Set fill style to white for visibility
    ctx.fillStyle = "white";
    
    // Draw ball
    ctx.beginPath();
    ctx.arc(gameState.ball.x, gameState.ball.y, 10, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw paddles
    ctx.fillRect(20, gameState.paddle1.y, 10, 100);
    ctx.fillRect(canvas.width - 30, gameState.paddle2.y, 10, 100);
    // ...existing code...
    requestAnimationFrame(animate);
}
animate();
