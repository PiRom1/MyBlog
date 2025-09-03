
    // Dungeon class. Support of the dungeon map. Contains array of the dungeon with the chests
    class Dungeon {
        constructor(dungeon_array) {
            this.dungeon_array = dungeon_array;
            this.tiles = this.get_tiles();
        }

        // Get a list of the tiles of the dungeon
        get_tiles() {
        
            let tiles = Array();
            let color;
            let type;
            for (let y = 0; y < this.dungeon_array.length; y++) {
                for (let x = 0; x < this.dungeon_array[0].length; x ++) {
                    if (this.dungeon_array[y][x] === 0) {
                        color = 'black';
                        type = 'wall';
                    }
                    else if (this.dungeon_array[y][x] === 1) {
                        color = 'white';
                        type = 'ground';
                    }
                    else if (this.dungeon_array[y][x] === 2) {
                        color = 'black';
                        type = 'chest';
                    }


                    let  pos_x = x;
                    let pos_y = y;
                
                    let tile = new Tile(pos_x, pos_y, TILE_WIDTH, TILE_HEIGHT, color, type);
                    tiles.push(tile);            
                }
            }

            return tiles;

        }


        is_ground(x,y) {
            return (this.dungeon_array[y][x] === 1)
        }


        // Draws the dungeon
        draw() {
            this.tiles.forEach(tile => {
                tile.draw();
            })
        }


    }

