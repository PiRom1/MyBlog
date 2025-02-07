// Setup canvas and websocket connection
const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');

let gameState = {
    ball: { x: 250, y: 150 },
    paddle1: { y: 100 },
    paddle2: { y: 100 }
};

const ws = new WebSocket('ws://localhost:8000/ws/pong/');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if(data.type === 'update'){
        // update state from backend
        gameState = { ...gameState, ...data.game_state };
    } else if(data.type === 'verify'){
        // Optionally compare local and backend positions, then adjust if necessary.
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
