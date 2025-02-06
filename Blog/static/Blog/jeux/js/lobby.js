document.addEventListener("DOMContentLoaded", function() {
  const lobbyElem = document.getElementById("lobby");
  const roomName = lobbyElem.dataset.roomName;
  const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
  const lobbySocket = new WebSocket(wsScheme + "://" + window.location.host + "/ws/lobby/" + roomName + "/");
  let isReady = false;

  lobbySocket.onopen = function() {
    console.log("Connected to lobby websocket for room:", roomName);
  };

  lobbySocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log("Websocket message:", data);
    if (data.waiting) {
      console.log("Updating waiting players : ", data.waiting);
      const playersElem = document.getElementById("players");
      playersElem.innerHTML = '';
      Object.keys(data.waiting).forEach(k => {
        const player = data.waiting[k];
        const playerDiv = document.createElement('div');
        playerDiv.className = 'player';
        playerDiv.textContent = `${player.name} - ${player.ready ? "Ready" : "Not Ready"}`;
        playersElem.appendChild(playerDiv);
      });
    }
  };

  lobbySocket.onclose = function() {
    console.log("Lobby websocket closed unexpectedly");
  };

  document.getElementById("readyButton").addEventListener("click", function() {
    if (!isReady) {
      lobbySocket.send(JSON.stringify({ action: "ready" }));
      this.textContent = "Not Ready";
      isReady = true;
    } else {
      lobbySocket.send(JSON.stringify({ action: "not_ready" }));
      this.textContent = "Ready";
      isReady = false;
    }
  });
});
