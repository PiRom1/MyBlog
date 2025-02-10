document.addEventListener("DOMContentLoaded", function() {
  const lobbyElem = document.getElementById("lobby");
  const roomName = lobbyElem.dataset.roomName;
  const gameName = lobbyElem.dataset.gameName;
  const gameSize = lobbyElem.dataset.gameSize;
  const gameType = lobbyElem.dataset.gameType;
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
  const lobbySocket = new WebSocket(wsScheme + "://" + window.location.host + "/ws/lobby/" + roomName + "/"+ gameName + "/" + gameSize + "/" + gameType + "/");
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
      // Replace fetch with form submission to trigger redirect.
      let form = document.createElement("form");
      form.method = "POST";
      form.action = '/play_lobby_game/' + data.token + '/';
      
      // CSRF token input
      let csrfInput = document.createElement("input");
      csrfInput.type = "hidden";
      csrfInput.name = "csrfmiddlewaretoken";
      csrfInput.value = csrfToken;
      form.appendChild(csrfInput);
      
      // roomName input
      let roomInput = document.createElement("input");
      roomInput.type = "hidden";
      roomInput.name = "roomName";
      roomInput.value = roomName;
      form.appendChild(roomInput);
      
      // team input
      let teamInput = document.createElement("input");
      teamInput.type = "hidden";
      teamInput.name = "team";
      teamInput.value = data.team;
      form.appendChild(teamInput);
      
      // role input
      let roleInput = document.createElement("input");
      roleInput.type = "hidden";
      roleInput.name = "role";
      roleInput.value = data.role;
      form.appendChild(roleInput);
      
      document.body.appendChild(form);
      form.submit();
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
