
    // Tile class : Base-design of the game, visual element to draw (wall or ground)
    class Tile {
        constructor(x, y, width, height, color, type) {
            this.x = x;
            this.y = y;
            this.width = width;
            this.height = height;
            this.color = color;
            this.type = type;
            this.image = this.get_image();
        }

        // Get image of the tile
        get_image() {
            let image = new Image();
            if (this.type === 'ground') {
                let i = randint(1, 4);
                image.src = `/static/img/dinocrypt/tiles/ground/ground_${i}.PNG`;
            }
            if (this.type === 'wall') {
                let i = randint(1, 3);
                image.src = `/static/img/dinocrypt/tiles/wall/wall_${i}.PNG`;            }
            
            return image;
        }

        // Draw image of the tile
        draw() {
            
            if (this.image.complete) { // s'assurer que l'image est chargée
                ctx.drawImage(this.image, this.x * this.width, this.y * this.height, this.width, this.height);
            }
            else {
                this.image.onload = () => {
                    ctx.drawImage(this.image, this.x * this.width, this.y * this.height, this.width, this.height);
                };
            }
        }

    }
