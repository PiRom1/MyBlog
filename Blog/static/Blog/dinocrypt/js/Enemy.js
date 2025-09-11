// Class for the Enemies


    class Enemy {

        constructor(x, y, player) {
            this.x = x;
            this.y = y;
            this.player = player;
            this.width = TILE_WIDTH;
            this.height = TILE_HEIGHT;
            this.color = 'tomato';
            this.is_moving = false;
            this.facing = 'down';
            this.image = new Image();
            this.get_image();
            
        }


        get_image() {
            
            if (this.facing === 'down') {
                this.image.src = `/static/img/dinocrypt/characters/front_1.png`;
            }
            if (this.facing === 'up') {
                this.image.src = `/static/img/dinocrypt/characters/back_1.png`;
            }
            if (this.facing === 'right') {
                this.image.src = `/static/img/dinocrypt/characters/right_1.png`;
            }
            if (this.facing === 'left') {
                this.image.src = `/static/img/dinocrypt/characters/left_1.png`;
            }
        }


        // Draw the Enemy
        draw() {
            this.get_image();
            // ctx.fillStyle = this.color;
            let pos_x = (this.x - this.player.offset_x) * this.width;
            let pos_y = (this.y - this.player.offset_y) * this.height;
            // ctx.fillRect(pos_x, pos_y, this.width, this.height);
            ctx.drawImage(this.image, pos_x, pos_y, this.width, this.height);
        }


        isCellFree(coords) {
            // console.log("array : ", array);
            // console.log(array[coords[0]][coords[1]])

            if (0 <= coords[0] < array.length && 0 <= coords[1] < array[0].length) {
                if (array[coords[0]][coords[1]] === 1) {
                    return true;
                }
            }
            return false;

        }



        getRandomMovement() {
            let movements = Array(Array(1, 0), Array(-1, 0), Array(0, 1), Array(0, -1));
            console.log("random movemernt:  ");
            movements.forEach(movement => {
                if (this.isCellFree([this.y + movement[0], this.x + movement[1]])) {
                    if (randint(1, 100) < 200) {
                        return movement;
                   }
                }
            })
        }


        get_movement(a_star, player_x, player_y) {

            if (Math.abs(player_x - this.x) + Math.abs(player_y - this.y) <= ENEMY_PATHFINDING_RADIUS) { // Alors on utilise A Star
                const movement = a_star.aStar(this.x, this.y, player_x, player_y);
                if (!movement) {
                    return this.getRandomMovement();
                    }
                console.log("Moving enemy to : ", movement[1]);
                return [movement[1][0] - this.x, movement[1][1] - this.y];
                
            }
            else { // Sinon, mouvement aléatoire   
                return this.getRandomMovement();
            }
        }


        // Move the player, or the dungeon of the offset is reached
        move(a_star) {

            if (this.is_moving) {
                return;
            }

            let movement = this.get_movement(a_star, this.player.x, this.player.y);
            
            if (movement) {
                this.is_moving = true;

                let [dx, dy] = movement


                if (dx === 1) {
                    this.facing = "right";
                }
                if (dx === -1) {
                    this.facing = "left";
                }
                if (dy === 1) {
                    this.facing = "down";
                }
                if (dy === -1) {
                    this.facing = "bottom";
                }
                
                if (this.is_moving) {

                    let frame = 0;

                    const animate = () => { // Animation de déplacement
                    
                        frame += 1;
                        this.x += dx / NB_MOVING_FRAMES;
                        this.y += dy / NB_MOVING_FRAMES;                  

                        if (frame < NB_MOVING_FRAMES) {
                            requestAnimationFrame(animate);
                            }
                        else {
                            this.x = Math.round(this.x);
                            this.y = Math.round(this.y);
                            this.is_moving = false;
                        }
                    };

                    requestAnimationFrame(animate);
                }
            }

        }


    }