// Class for the player. Can draw and move the player
    class Player {

        constructor() {
            
            this.offset_x = 0; // Le décalage entre la vraie position et la position affichée sur l'écran (car on ne voit pas tout le donjon à la fois)
            this.offset_y = 0;
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


        get_start_pos(start_coord, dungeon) {

            if (start_coord[1] > TILES_PER_ROW) {
                this.x = start_coord[1];
                this.offset_x = start_coord[1] - 5;
            }
            else {
                this.x = start_coord[1];
            }

            if (start_coord[0] > TILES_PER_COLUMN) {
                this.y = start_coord[1];
                this.offset_y = start_coord[0] - 5;
            }
            else {
                this.y = start_coord[0];
            }

        

            dungeon.tiles.forEach(tile => {
                                tile.x -= this.offset_x;
                                tile.y -= this.offset_y;
                            })
            
        }


        // Draw the player
        draw() {
            this.get_image();
            // ctx.fillStyle = this.color;
            let pos_x = (this.x - this.offset_x) * this.width;
            let pos_y = (this.y - this.offset_y) * this.height;
            // ctx.fillRect(pos_x, pos_y, this.width, this.height);
            ctx.drawImage(this.image, pos_x, pos_y, this.width, this.height);
        }


        // Move the player, or the dungeon of the offset is reached
        move(movement, dungeon) {

            if (this.is_moving) {
                return;
            }

            minimap.discover(this.x, this.y);

            let offset_x_value = 0;
            let offset_y_value = 0;
            let x_value = 0;
            let y_value = 0;
            let tile_x = 0;
            let tile_y = 0;

            if (movement === 'right') {
                this.facing = 'right';
                if (dungeon.is_ground(Math.round(this.x + 1), Math.round(this.y))) {
                    if (this.x - this.offset_x >= TILES_PER_ROW - MOVE_THRESHOLD_X) {
                        tile_x = -1;
                        offset_x_value = 1;
                    }
                        x_value = 1;
                    this.is_moving = true;
                }
            }


            if (movement === 'left') {
                this.facing = 'left';
                if (dungeon.is_ground(Math.round(this.x - 1), Math.round(this.y))) {
                    if (this.x - this.offset_x < MOVE_THRESHOLD_X) {
                        tile_x = 1;
                        offset_x_value = -1;
                    }
                    x_value = -1;
                this.is_moving = true;
                }
            }
            

            if (movement === 'down') {
                this.facing = 'down';
                if (dungeon.is_ground(Math.round(this.x), Math.round(this.y + 1))) {
                    if (this.y - this.offset_y >= TILES_PER_COLUMN - MOVE_THRESHOLD_y) {
                        tile_y = -1;
                        offset_y_value = 1;
                    }
                    y_value = 1;
                this.is_moving = true;
                }
            }


            if (movement === 'up') {
                this.facing = 'up';
                if (dungeon.is_ground(Math.round(this.x), Math.round(this.y - 1))) {
                    if ((this.y - this.offset_y) <= MOVE_THRESHOLD_y) {
                        tile_y = 1;
                        offset_y_value = -1;
                    }
                    y_value = -1;
                this.is_moving = true;
                }
            }


           
            
            if (this.is_moving) {

                let frame = 0;

                const animate = () => { // Animation de déplacement
                    if (offset_x_value + offset_y_value !== 0) {
                        dungeon.tiles.forEach(tile => {
                                tile.x += tile_x / NB_MOVING_FRAMES;
                                tile.y += tile_y / NB_MOVING_FRAMES;
                            })
                        }
                    
                        

                    frame += 1;
                    this.x += x_value / NB_MOVING_FRAMES;
                    this.y += y_value / NB_MOVING_FRAMES;
                    this.offset_x += offset_x_value / NB_MOVING_FRAMES;
                    this.offset_y += offset_y_value / NB_MOVING_FRAMES;

                    

                    if (frame < NB_MOVING_FRAMES) {
                        requestAnimationFrame(animate);
                        }
                    else {
                        this.x = Math.round(this.x);
                        this.y = Math.round(this.y);
                        this.offset_x = Math.round(this.offset_x);
                        this.offset_y = Math.round(this.offset_y);
                        this.is_moving = false;
                    }
                };

                requestAnimationFrame(animate);
            }

            console.log(`offset x : ${this.offset_x} / offset y : ${this.offset_y} / pos_x : ${this.x} / pos_y : ${this.y}`)


        }


    }