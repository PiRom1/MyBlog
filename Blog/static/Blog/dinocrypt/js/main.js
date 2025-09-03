document.addEventListener('DOMContentLoaded', function() {

    // Events
    let keys = {};
    document.addEventListener("keydown", (e) => {
        keys[e.key] = true;
    });

    document.addEventListener("keyup", (e) => {
        keys[e.key] = false;
    });


    




    // Get data
    const data = document.getElementById('data');
    const array = JSON.parse(data.getAttribute("dungeon"));
    const start_coord = JSON.parse(data.getAttribute("start_coord"));


    // Initialize dungeon and player
    const dungeon = new Dungeon(array);
    const player = new Player();
    player.get_start_pos(start_coord, dungeon);

    // Minimap
    minimap = new Minimap(MINIMAP_X_MIN_COORD, 
                          MINIMAP_X_MAX_COORD, 
                        MINIMAP_Y_MIN_COORD, 
                        MINIMAP_Y_MAX_COORD, 
                        MINIMAP_TILE_WIDTH, 
                        MINIMAP_TILE_HEIGHT, 
                        array);
    


    // Fonction qui dessine le jeu complet
    function drawGame() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        dungeon.draw();
        player.draw();
        minimap.draw();
    }

    // La boucle principale du jeu (appelée à chaque frame)
    function gameLoop() {
       

        // Move character
        move_right.forEach(key => {
            if (keys[key]) {
                player.move("right", dungeon);
            }
        });

        move_left.forEach(key => {
            if (keys[key]) {
                player.move("left", dungeon);
            }
        });

        move_up.forEach(key => {
            if (keys[key]) {
                player.move("up", dungeon);
            }
        });

        move_down.forEach(key => {
            if (keys[key]) {
                player.move("down", dungeon);
            }
        });
        

        drawGame();
        // Appelle gameLoop de nouveau au prochain rafraîchissement
        requestAnimationFrame(gameLoop);
    }

    // Démarrage de la boucle d’animation
    gameLoop();


});

