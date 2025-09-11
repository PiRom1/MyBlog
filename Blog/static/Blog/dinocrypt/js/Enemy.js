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


        



        getRandomMovement(taken_cells) {
            let movements = Array(Array(1, 0), Array(-1, 0), Array(0, 1), Array(0, -1));
            for (let movement of movements) {
                if (isCellFree([this.y + movement[1], this.x + movement[0]], taken_cells, this.player.x, this.player.y)) {
                    if (randint(1, 100) < 20) {
                        return movement;
                   }
                }
            }
        }


        get_movement(a_star, taken_cells) {

            if (Math.abs(this.player.x - this.x) + Math.abs(this.player.y - this.y) <= ENEMY_PATHFINDING_RADIUS) { // Alors on utilise A Star
                const movement = a_star.aStar(this.x, this.y, this.player.x, this.player.y, taken_cells);
                if (!movement) {
                    return this.getRandomMovement(taken_cells);
                    }
                console.log(movement);
                return [movement[1][0] - this.x, movement[1][1] - this.y];
                
            }
            else { // Sinon, mouvement aléatoire   
                return this.getRandomMovement(taken_cells);
            }
        }


        // Move the player, or the dungeon of the offset is reached
        move(a_star, taken_cells) {
            if (this.is_moving) {
                return;
            }

            let movement = this.get_movement(a_star, taken_cells);
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
                    this.facing = "up";
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