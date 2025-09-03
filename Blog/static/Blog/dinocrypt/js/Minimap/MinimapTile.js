
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
            this.color = "#d8b54200";
        }
        if (this.type === "wall") {
            this.color = "#342d2f00";
        }
        if (this.type === "ground") {
            this.color = "#736b6d00";
        }
        if (this.type === "player") {
            this.color = "#e3625100";
        }
    }


    // Draw image of the tile
    draw() {
        ctx.fillStyle = this.color;  // couleur du carré
        ctx.fillRect(this.pos_x, this.pos_y, this.width, this.height); 
        // console.log("Drawing tile of color ", this.color, " at pos ", this.pos_x, this.pos_y);
        }
    

    }
