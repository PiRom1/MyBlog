document.addEventListener('DOMContentLoaded', function() {

    




    // Get data
    const data = document.getElementById('data');
    const array = JSON.parse(data.getAttribute("dungeon"));
    const start_coord = JSON.parse(data.getAttribute("start_coord"));
    console.log("donjon : ", array);
    console.log("start coord : ", start_coord);


    // Initialize dungeon and player
    const dungeon = new Dungeon(array);
    const player = new Player();
    player.get_start_pos(start_coord, dungeon);


    // Déplacement du joueur, déclenché par le clavier
    document.addEventListener('keydown', function(e) {
        player.move(e.key, dungeon);
    });

    // Fonction qui dessine le jeu complet
    function drawGame() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        dungeon.draw();
        player.draw();
    }

    // La boucle principale du jeu (appelée à chaque frame)
    function gameLoop() {
        drawGame();
        // Appelle gameLoop de nouveau au prochain rafraîchissement
        requestAnimationFrame(gameLoop);
    }

    // Démarrage de la boucle d’animation
    gameLoop();


});

