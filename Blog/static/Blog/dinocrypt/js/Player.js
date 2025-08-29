// Class for the player. Can draw and move the player
    class Player {

        constructor() {
            
            this.offset_x = 0; // Le décalage entre la vraie position et la position affichée sur l'écran (car on ne voit pas tout le donjon à la fois)
            this.offset_y = 0;
            this.width = TILE_WIDTH;
            this.height = TILE_HEIGHT;
            this.color = 'tomato';
            
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

            console.log("Get start pos ... ");
            console.log("offset x/y : ", this.offset_x, this.offset_y);

            dungeon.tiles.forEach(tile => {
                                // console.log("tile x/y : ", tile.x, tile.y);
                                tile.x -= this.offset_x;
                                tile.y -= this.offset_y;
                            })
            
                        
            
        }


        // Draw the player
        draw() {
            ctx.fillStyle = this.color;
            let pos_x = (this.x - this.offset_x) * this.width;
            let pos_y = (this.y - this.offset_y) * this.height;
            ctx.fillRect(pos_x, pos_y, this.width, this.height);
        }


        // Move the player, or the dungeon of the offset is reached
        move(key, dungeon) {

            let offset_x_value = 0;
            let offset_y_value = 0;
            let x_value = 0;
            let y_value = 0;
            let tile_x = 0;
            let tile_y = 0;
            let is_moving = false;

            if (key === 'ArrowRight') {
                if (dungeon.is_ground(Math.round(this.x + 1), Math.round(this.y))) {
                    console.log("going to ground");
                    if (this.x - this.offset_x >= TILES_PER_ROW - MOVE_THRESHOLD_X) {
                        tile_x = -1;
                        offset_x_value = 1;
                    }
                        x_value = 1;
                    is_moving = true;
                }
                else {
                    console.log("going to wall");
                }
            }


            if (key === 'ArrowLeft') {
                if (dungeon.is_ground(Math.round(this.x - 1), Math.round(this.y))) {
                    console.log("going to ground");
                    if (this.x - this.offset_x < MOVE_THRESHOLD_X) {
                        tile_x = 1;
                        offset_x_value = -1;
                    }
                    x_value = -1;
                is_moving = true;
                }
                else {
                    console.log("going to wall");
                }
            }
            

            if (key === 'ArrowDown') {
                if (dungeon.is_ground(Math.round(this.x), Math.round(this.y + 1))) {
                    console.log("going to ground");
                    if (this.y - this.offset_y >= TILES_PER_COLUMN - MOVE_THRESHOLD_y) {
                        tile_y = -1;
                        offset_y_value = 1;
                    }
                    y_value = 1;
                is_moving = true;
                }
                else {
                    console.log("going to wall");
                }
            }


            if (key === 'ArrowUp') {
                if (dungeon.is_ground(Math.round(this.x), Math.round(this.y - 1))) {
                    console.log("going to ground");
                    if ((this.y - this.offset_y) <= MOVE_THRESHOLD_y) {
                        tile_y = 1;
                        offset_y_value = -1;
                    }
                    y_value = -1;
                is_moving = true;
                }
                else {
                    console.log("going to wall");
                }
            }
            
            if (is_moving) {

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
                    }
                };

                requestAnimationFrame(animate);
            }

            console.log(`offset x : ${this.offset_x} / offset y : ${this.offset_y} / pos_x : ${this.x} / pos_y : ${this.y}`)


        }


    }