document.addEventListener('DOMContentLoaded', async function () {

    const leaderboards = document.querySelectorAll('.leaderboard');
    const show_leaderboards = document.querySelectorAll('.show_leaderboard');
    const game_selector = document.getElementById('game-selector');
    const timedelta_selector = document.getElementById('timedelta-selector');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    function filter_leaderboards() {
        leaderboards.forEach(leaderboard => {
            if ( (leaderboard.getAttribute('name') === game_selector.value) && (leaderboard.getAttribute('timedelta') === timedelta_selector.value) ) {
                leaderboard.style.display = 'block';
            }
            else {
                leaderboard.style.display = 'none';
            }
        });
    };

    filter_leaderboards();

    show_leaderboards.forEach(item => {
        item.addEventListener('click', function() {
            game_selector.value = item.getAttribute('name');
            filter_leaderboards();
        });
    });

    game_selector.addEventListener('change', function() {
        filter_leaderboards();
    });

    timedelta_selector.addEventListener('change', function() {
        filter_leaderboards();
    });

    // New code: Fetch and display open lobbies dynamically.
    async function fetchLobbies() {
        try {
            const response = await fetch('/get_open_lobbies/');
            const data = await response.json();
            const lobbyContainer = document.getElementById('open-lobbies');
            let lobbyHTML = '';
            if (data.lobbies && data.lobbies.length > 0) {
                lobbyHTML = '<ul>';
                data.lobbies.forEach(lobby => {
                    // Each lobby rendered as a link with href and a data attribute
                    lobbyHTML += `<li><a href="/lobby/${lobby.name}" data-room-name="${lobby.name}">${lobby.name} - ${lobby.game}</a></li>`;
                });
                lobbyHTML += '</ul>';
            } else {
                lobbyHTML = '<p>Aucun lobby ouvert</p>';
            }
            lobbyContainer.innerHTML += lobbyHTML;

            // Add event listener for lobby links to establish WebSocket join connection
            lobbyContainer.addEventListener('click', function(e) {
                const target = e.target;
                if (target.tagName.toLowerCase() === 'a') {
                    window.location.href = "/lobby/" + roomName;
                }
            });
        } catch (error) {
            console.error('Erreur lors du fetch des lobbies :', error);
        }
    }
    fetchLobbies();
    
    const createLobbyForm = document.getElementById('create-lobby-form');
    if (createLobbyForm) {
        console.log("Create lobby form found.");
        createLobbyForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const lobbyName = document.getElementById('lobby-name-input').value;
            const game = document.getElementById('lobby-game-selector').value;
            try {
                const response = await fetch('/create_lobby/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken  // Using the constant defined above
                    },
                    body: JSON.stringify({ lobby: lobbyName, game: game })
                });
                const resData = await response.json();
                console.log("Lobby creation response:", resData);
                if (resData.success) {
                    window.location.href = "/lobby/" + lobbyName;
                } else {
                    console.error("Lobby creation failed:", resData.error);
                }
            } catch (error) {
                console.error("Error creating lobby:", error);
            }
        });
    }
});