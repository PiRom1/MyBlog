// Setup canvas and websocket connection
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');

let gameState = {
    ball: { x: 400, y: 250 },
    paddle1: { y: 200 },
    paddle2: { y: 200 }
};

// Declare animationFrameId at the top
let animationFrameId;

// Retrieve room name from the DOM
const roomElem = document.querySelector('.game-container');
const roomName = roomElem ? roomElem.dataset.roomName : 'default';
// Update WebSocket connection URL to be relative:
const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
let ws; // Declare globally
const countdown = document.getElementById("countdown");

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

// Set canvas border based on player's team color
if(gameData.team === '1'){
    canvas.style.border = "5px solid skyblue";
    document.getElementById('player-team').textContent = 'Blue';
    document.getElementById('player-team').style.color = "skyblue";
} else{
    canvas.style.border = "5px solid #ff6600";
    document.getElementById('player-team').textContent = 'Orange';
    document.getElementById('player-team').style.color = "#ff6600";
}

function connectWebSocket() {
    ws = new WebSocket(`${ws_scheme}://${window.location.host}/ws/pong/${roomName}/`);
    
    ws.onopen = function() {
        console.log("Connected to game websocket for room:", roomName);
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
    
    ws.onclose = function(event) {
        console.log("Disconnected from game websocket");
        console.log("close code:", event.code, "reason:", event.reason);
        if (gameState.game_finished) {
            return;
        } else if (event.code === 1006) {
            console.log("trying to reconnect");
            countdown.textContent = "Trying to reconnect ";
            countdown.style.display = "block";
            setTimeout(() => {
                connectWebSocket();
            }, 1000);
        }
    };
    
    ws.onmessage = function(event) {
        // ...existing onmessage code...
        const data = JSON.parse(event.data);
        if(data.type === 'game_update'){
            // ...existing update logic...
            gameState = { ...gameState, ...data.game_state };
            // update score display if available in gameState
            if(document.getElementById('score1') && document.getElementById('score2')) {
                document.getElementById('score1').textContent = gameState.score.team1;
                document.getElementById('score2').textContent = gameState.score.team2;
            }
        } else if(data.type === 'print_cache'){
            console.log("cache : ",data.cache);
        } else if(data.type === 'start_game'){
            console.log("Game started", data.game_state);
            gameState = { ...gameState, ...data.game_state };
            if(document.getElementById('score1') && document.getElementById('score2')) {
                document.getElementById('score1').textContent = gameState.score.team1;
                document.getElementById('score1').style.color = "skyblue";
                document.getElementById('score2').textContent = gameState.score.team2;
                document.getElementById('score2').style.color = "#ff6600";
            }
        } else if(data.type === 'all_players_connected'){
            console.log("All players connected: " + data.message);
            // ...existing countdown code...
            let count = 3;
            countdown.textContent = "Le jeu va démarrer dans " + count;
            countdown.style.display = "block";
            const countdownPromise = new Promise((resolve) => {
                const countdownInterval = setInterval(() => {
                    count--;
                    countdown.textContent = "Le jeu va démarrer dans " + count;
                    if (count <= 0) {
                        clearInterval(countdownInterval);
                        countdown.style.display = "none";
                        resolve();
                    }
                }, 1000);
            });
            countdownPromise.then(() => {
                ws.send(JSON.stringify({ type: 'start_game'}));
            });
        } else if(data.type === 'game_finished'){
            cancelAnimationFrame(animationFrameId);
            ctx.clearRect(0,0, canvas.width, canvas.height);
            ctx.fillStyle = "white";
            ctx.font = "30px Arial";
            ctx.fillText("Game Over", 300, 200);
            ctx.font = "20px Arial";
            ctx.fillText("Final Score", 320, 250);
            ctx.fillText("Team Blue: " + gameState.score.team1, 320, 280);
            ctx.fillText("Team Orange: " + gameState.score.team2, 320, 310);
            console.log("Game over: " + data.message);
            const button = document.createElement("button");
            button.textContent = "Retour";
            button.style.position = "absolute";
            button.style.left = "50%";
            button.style.transform = "translate(-50%, -50%)";
            button.onclick = () => {
                window.location.href = "/jeux";
            };
            document.body.appendChild(button);
        }
    };
}

// Remove original websocket instantiation and call connectWebSocket() to start the connection:
connectWebSocket();

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
    
    // Set fill style to white for ball drawing
    ctx.fillStyle = "white";
    
    // Draw ball
    ctx.beginPath();
    ctx.arc(gameState.ball.x, gameState.ball.y, 10, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw left paddle (Team Blue) and right paddle (Team Red)
    ctx.fillStyle = "skyblue";
    ctx.fillRect(20, gameState.paddle1.y, 10, 100);
    ctx.fillStyle = "#ff6600";
    ctx.fillRect(canvas.width - 30, gameState.paddle2.y, 10, 100);
    // ...existing code...
    animationFrameId = requestAnimationFrame(animate);
}
animate();
