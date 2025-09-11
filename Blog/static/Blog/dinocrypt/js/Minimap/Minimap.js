
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
        this.player_color = MINIMAP_PLAYER_TILE_COLOR;

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
                    let type = "border";
                    if ((x !== 0) && (y !== 0) && (x !== this.dungeon[0].length - 1) && (y !== this.dungeon.length - 1)) {
                        type = this.type_dict[this.dungeon[y][x]]
                    }
                   
                    let tile = new MinimapTile(x, y, pos_x, pos_y, this.tile_width, this.tile_height, type);
                    if ((x === 0) || (y === 0)) {
                        tile.type = "border";
                    }
                    this.tiles.push(tile);
                }
            }   
    }


    actualize() {
        this.tiles.forEach(tile => {
            let [pos_y, pos_x] = this.compute_pos(tile.y,tile.x);
            tile.pos_x = pos_x;
            tile.pos_y = pos_y;
        })
    }


    discover(x, y) {
        // console.log("actualisation minimap, découverte des cases proximales : ", x, y);
        this.tiles.forEach(tile => {
            if (distance(x, y, tile.x, tile.y) < 8) {
                tile.color = tile.color.slice(0, -2) + "ff"; // remplace les 2 derniers caractères par "ff"
            }
        })
    }


    draw_player(x, y) {
        let [pos_y, pos_x] = this.compute_pos(y, x);
        pos_y -= this.tile_height/2;
        pos_x -= this.tile_width/2;
        
        if (lap%(MINIMAP_BLINKING_PLAYER_RATE*2) < MINIMAP_BLINKING_PLAYER_RATE) { // Toutes les 35 frames environ
            this.player_color = this.player_color.slice(0, -2) + "ff"; // remplace les 2 derniers caractères par "ff"
        }
        else {
            this.player_color = this.player_color.slice(0, -2) + "33"; // remplace les 2 derniers caractères par "ff"
        }


        ctx.fillStyle = this.player_color;  // couleur du carré
        ctx.fillRect(pos_x, pos_y, this.tile_width*2, this.tile_height*2); 


    }

    draw(player_x, player_y) {
        this.tiles.forEach(tile => {
            tile.draw();
        })
        this.draw_player(player_x, player_y);
    }



}
