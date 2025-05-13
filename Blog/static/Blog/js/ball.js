console.log('drawing ...');


function draw() {

    console.log('drawing ...');

    function randint(a, b) {
        let nb = a + (Math.random() * (b-a));
        return nb;
    }


    function get_distance(x0, y0, x1, y1) {
        d = Math.sqrt((x0 - x1)**2 + (y0 - y1)**2);
        return d;
    }


    function norm(x, y) {
        return Math.sqrt((y - x)**2)
    }

    class Circle {

        constructor(x0, y0, radius, color, canvas) {
        this.x = x0;
        this.y = y0;
        this.dx = 0;
        this.dy = 0;
        this.radius = radius;
        this.canvas = canvas;
        this.context = this.canvas.getContext("2d");
        
        this.alpha = ALPHA_RANGE;
        this.color = color;
        
        }


        gravity() {

            this.dy += GRAVITY;

        }

        move() {
            if (get_distance(this.x, this.y, contour.x, contour.y) >= CONTOUR_RADIUS - RADIUS) {
                this.compute_new_angle();
            }

            this.x += this.dx;
            this.y += this.dy;

        }

        compute_new_angle() {
            // Get alpha
            

            new_dx = norm(this.dx, this.dy) * Math.cos(alpha);
            new_dx = norm(this.dx, this.dy) * Math.sin(alpha) * -1;
            
        }

        draw() {

            let r = parseInt(this.color.slice(1, 3), 16);
            let g = parseInt(this.color.slice(3, 5), 16);
            let b = parseInt(this.color.slice(5, 7), 16);

            this.context.beginPath();
            this.context.fillStyle = 'rgba(' + r + ',' + g + ',' + b + ',' + this.alpha + ')';
            this.context.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
            this.context.fill(); 
            }
        }
    
    

    const ALPHA_RANGE = 0.8;
    const RADIUS = 10;
    const BG_COLOR = "#F09228";
    const GRAVITY = 0.2;



    console.log('Script network')
        
    // Initialize variables
    let canvas = document.getElementById("canvas2");
    var context = canvas.getContext("2d");

    const CONTOUR_RADIUS = Math.min(canvas.width/2, canvas.height/2) - 10;

    let circle = new Circle(randint(RADIUS, CONTOUR_RADIUS) + 80, randint(RADIUS, CONTOUR_RADIUS) + 30, RADIUS, '#e5437', canvas);
    let contour = new Circle(canvas.width/2, canvas.height/2, CONTOUR_RADIUS, '#ffffff', canvas);

    contour.draw();
    circle.draw();
    function loop() {

        context.fillStyle = BG_COLOR;
        context.fillRect(0, 0, canvas.width, canvas.height);
        contour.draw();
        circle.gravity();
        circle.move();

        circle.draw();
        


        // Refaire l'animation
        requestAnimationFrame(loop);
        }
        
        
        
        // Démarrer l'animation
        loop();
        
        
    }


draw();

