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
// Update WebSocket connection URL to include the room name
const ws = new WebSocket(`ws://localhost:8000/ws/pong/${roomName}/`);

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if(data.type === 'game_update'){
        // update state from backend using new type
        gameState = { ...gameState, ...data.game_state };
    } else if(data.type === 'start_game'){
        // Initialize game state if required
        console.log("Game started", data.game_state);
        gameState = { ...gameState, ...data.game_state };
    } else if(data.type === 'all_players_connected'){
        // All players are connected; can display a message or unpause the game 
        console.log("All players connected: " + data.message);
    } else if(data.type === 'verify'){
        // Optionally compare local and backend positions
        // ...existing verification logic...
    }
};

// Send key events to backend
document.addEventListener('keydown', (e) => {
    ws.send(JSON.stringify({ type: 'key_input', key: e.key, action: 'down' }));
});
document.addEventListener('keyup', (e) => {
    ws.send(JSON.stringify({ type: 'key_input', key: e.key, action: 'up' }));
});

// Local animation loop for smooth drawing
function animate() {
    // ...existing code...
    ctx.clearRect(0,0, canvas.width, canvas.height);
    // Draw ball
    ctx.beginPath();
    ctx.arc(gameState.ball.x, gameState.ball.y, 10, 0, Math.PI*2);
    ctx.fill();
    // Draw paddles
    ctx.fillRect(20, gameState.paddle1.y, 10, 100);
    ctx.fillRect(canvas.width - 30, gameState.paddle2.y, 10, 100);
    // ...existing code...
    requestAnimationFrame(animate);
}
animate();
