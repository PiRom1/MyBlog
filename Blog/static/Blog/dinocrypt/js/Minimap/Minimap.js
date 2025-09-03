X_MIN_COORD = 600;
X_MAX_COORD = 1800;
Y_MIN_COORD = 500;
Y_MAX_COORD = 1000


class Minimap {
    constructor(x_min_coord, x_max_coord, y_min_coord, y_max_coord, tile_width, tile_height, dungeon) {
        this.x_min_coord = x_min_coord;
        this.x_max_coord = x_max_coord;
        this.y_min_coord = y_min_coord;
        this.y_max_coord = y_max_coord;
        this.tile_width = tile_width;
        this.tile_height = tile_height;
        this.dungeon = dungeon;
        this.type_dict = {0 : "wall", 1 : "ground", 2 : "chest"}
        this.get_tiles();
    }


    compute_pos(y, x) {
        let pos_y = this.y_min_coord + this.tile_height * y;
        let pos_x = this.x_min_coord + this.tile_width * x;


        return [pos_y, pos_x];
    }

    get_tiles() {
        this.tiles = Array();
        for (let y = 0; y < this.dungeon.length; y++) {
                for (let x = 0; x < this.dungeon[0].length; x ++) {
                    let [pos_y, pos_x] = this.compute_pos(y,x);
                    let tile = new MinimapTile(x, y, pos_x, pos_y, this.tile_width, this.tile_height, this.type_dict[this.dungeon[y][x]]);
                    this.tiles.push(tile);
                }
            }
            
        
    }

    draw() {
        this.tiles.forEach(tile => {
            tile.draw();
        })
    }



}
