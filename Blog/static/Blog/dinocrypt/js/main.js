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

    //// AStar
    const a_star = new AStar(array);
    



    // Initialize dungeon and player
    const dungeon = new Dungeon(array);
    const player = new Player();
    player.get_start_pos(start_coord, dungeon);

    const enemies = Array();
    const enemies_coords = JSON.parse(data.getAttribute("ennemies_coord"));

    enemies_coords.forEach(enemy_coord => {
        enemies.push(new Enemy(enemy_coord[1], enemy_coord[0], player));
        array[enemy_coord[0]][enemy_coord[1]] = -2;
    })


    // Minimap
    minimap = new Minimap(MINIMAP_X_MIN_COORD, 
                          MINIMAP_X_MAX_COORD, 
                        MINIMAP_Y_MIN_COORD, 
                        MINIMAP_Y_MAX_COORD, 
                        MINIMAP_TILE_WIDTH, 
                        MINIMAP_TILE_HEIGHT, 
                        array);
    minimap.discover(start_coord[1], start_coord[0]);
    


    // Fonction qui dessine le jeu complet
    function drawGame() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        dungeon.draw();
        player.draw();
        minimap.draw(player.x, player.y, enemies);
        enemies.forEach(enemy => {
            enemy.draw();
        })
        
    }


    // Fonction qui fait se déplacer les entités
    function moveGame(player_movement) {
        player.move(player_movement, dungeon);
        if (player.is_moving) {
            enemies.forEach(enemy => {
                console.log(`Previous pos : ${enemy.x} / ${enemy.y}`);
                array[Math.round(enemy.x)][Math.round(enemy.y)] = 1; // Free cell
                enemy.move(a_star);
                console.log("enemy : ", enemy)
                array[Math.round(enemy.x)][Math.round(enemy.y)] = -2;
                console.log(`New pos : ${enemy.x} / ${enemy.y}`);
            })
            count = {}
            array.flat().forEach(val => count[val] = count[val] ? count[val] + 1 : 1)

            console.log(`Nombre d'ennemis : ${count[-2]}`)
        };

    }

    // La boucle principale du jeu (appelée à chaque frame)
    function gameLoop() {

        let player_movement = false;
        // Move character
        move_right.forEach(key => {
            if (keys[key]) {
                player_movement = "right";
            }
        });

        move_left.forEach(key => {
            if (keys[key]) {
                player_movement = "left";
            }
        });

        move_up.forEach(key => {
            if (keys[key]) {
                player_movement = "up";
            }
        });

        move_down.forEach(key => {
            if (keys[key]) {
                player_movement = "down";
            }
        });
        

        moveGame(player_movement);
        drawGame();
        
        // Appelle gameLoop de nouveau au prochain rafraîchissement
        requestAnimationFrame(gameLoop);

        lap += 1;
    }

    // Démarrage de la boucle d’animation
    gameLoop();


});

