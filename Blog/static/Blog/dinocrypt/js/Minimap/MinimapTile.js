
class MinimapTile {
    constructor(x, y, pos_x, pos_y, width, height, type) {
        this.x = x;
        this.y = y;
        this.pos_x = pos_x;
        this.pos_y = pos_y;
        this.width = width;
        this.height = height;
        this.type = type;
        this.color = "rgba(0, 0, 0, 0.52)"; // Default color
        this.get_color();
    }

    // Get Tile color according to its type
    get_color() {
        if (this.type === "chest") {
            this.color = MINIMAP_CHEST_TILE_COLOR;
        }
        if (this.type === "wall") {
            this.color = MINIMAP_WALL_TILE_COLOR;
        }
        if (this.type === "ground") {
            this.color = MINIMAP_GROUND_TILE_COLOR;
        }
        if (this.type === "border") {
            this.color = MINIMAP_BORDER_TILE_COLOR;
        }
        if (this.type === "enemy") {
            this.color = MINIMAP_ENEMY_TILE_COLOR;
        }
    }


    // Draw image of the tile
    draw() {
        ctx.fillStyle = this.color;  // couleur du carré
        ctx.fillRect(this.pos_x, this.pos_y, this.width, this.height); 
        // console.log("Drawing tile of color ", this.color, " at pos ", this.pos_x, this.pos_y);
        }
    

    }
