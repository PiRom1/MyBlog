document.addEventListener("DOMContentLoaded", function() {
  const lobbyElem = document.getElementById("lobby");
  const roomName = lobbyElem.dataset.roomName;
  const gameName = lobbyElem.dataset.gameName;
  const gameSize = lobbyElem.dataset.gameSize;
  const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
  const lobbySocket = new WebSocket(wsScheme + "://" + window.location.host + "/ws/lobby/" + roomName + "/"+ gameName + "/" + gameSize + "/");
  let isReady = false;

  lobbySocket.onopen = function() {
    console.log("Connected to lobby websocket for room:", roomName);
  };

  lobbySocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log("Websocket message:", data);
    if (data.players) {
      console.log("Updating waiting players : ", data.players);
      const playersElem = document.getElementById("players");
      playersElem.innerHTML = '';
      Object.keys(data.players).forEach(k => {
        const player = data.players[k];
        const playerDiv = document.createElement('div');
        playerDiv.className = 'player';
        playerDiv.textContent = `${player.name} - ${player.ready ? "Ready" : "Not Ready"}`;
        playersElem.appendChild(playerDiv);
      });
    }

    if (data.type === "all_ready") {
      // Décompte de 3 secondes avant de rediriger vers le jeu
      let count = 3;
      const countdown = document.getElementById("countdown");
      countdown.textContent = "Le jeu va démarrer dans " + count;
      countdown.style.display = "block";
      const countdownInterval = setInterval(() => {
        count--;
        countdown.textContent = "Le jeu va démarrer dans " + count;
        if (count <= 0) {
          clearInterval(countdownInterval);
        }
      }, 1000);
    }
    
    if (data.type === "start_game") {
      window.location.href = "/jeux/" ;
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
