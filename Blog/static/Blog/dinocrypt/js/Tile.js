// Tile class : Base-design of the game, visual element to draw (wall or ground)
class Tile {
    constructor(x, y, width, height, color, type) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.color = color;
        this.type = type;

        // on stocke séparément les images si c'est un chest
        if (this.type === "chest") {
            this.groundImage = this.get_random_image("ground", 4);
            this.chestImage = this.get_random_image("chest", 3);
        } else {
            this.image = this.get_image();
        }
    }

    // helper pour charger une image
    get_random_image(category, maxIndex) {
        let image = new Image();
        let i = randint(1, maxIndex);
        image.src = `/static/img/dinocrypt/tiles/${category}/${category}_${i}.PNG`;
        return image;
    }

    // Get image of the tile
    get_image() {
        if (this.type === "ground") {
            return this.get_random_image("ground", 4);
        }
        if (this.type === "wall") {
            return this.get_random_image("wall", 3);
        }
        if (this.type === "chest") {
            // ce cas est géré dans le constructeur
            return null;
        }
    }

    // Draw image of the tile
    draw() {
        if (this.type === "chest") {
            // d'abord le sol
            if (this.groundImage.complete) {
                ctx.drawImage(this.groundImage, this.x * this.width, this.y * this.height, this.width, this.height);
            } else {
                this.groundImage.onload = () => {
                    ctx.drawImage(this.groundImage, this.x * this.width, this.y * this.height, this.width, this.height);
                };
            }

            // puis le coffre
            if (this.chestImage.complete) {
                ctx.drawImage(this.chestImage, this.x * this.width, this.y * this.height, this.width, this.height);
            } else {
                this.chestImage.onload = () => {
                    ctx.drawImage(this.chestImage, this.x * this.width, this.y * this.height, this.width, this.height);
                };
            }
        } else {
            if (this.image.complete) {
                ctx.drawImage(this.image, this.x * this.width, this.y * this.height, this.width, this.height);
            } else {
                this.image.onload = () => {
                    ctx.drawImage(this.image, this.x * this.width, this.y * this.height, this.width, this.height);
                };
            }
        }
    }
}
