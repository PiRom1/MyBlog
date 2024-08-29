// Position initiale et vitesse du cercle
let x0 = 80;
let y0 = 80;
let vitesse = 1;  // Vitesse max

let n_circles = 50;
let radius = 10;

let x = x0;
let y = y0;

let mouseX = NaN;
let mouseY = NaN;
let BG_COLOR = '#cd1040';
let CIRCLE_COLOR = '#e0e0e0';
let LINK_COLOR = [246, 246, 246];
let repulsion = 0.75;

let distance = 150;

let SHAPES = [0, 1];


function get_mouse_pos(event){
    posx = event.clientX;
    posy = event.clientY;
    return posx, posy
}


function randint(a, b) {
    let nb = a + (Math.random() * (b-a));
    return nb;
}

function f(x) {
    return(1 - (1/distance) * x);
}


function get_distance(x0, y0, x1, y1) {
    d = Math.sqrt((x0 - x1)**2 + (y0 - y1)**2);
    return d;
}





function get_links(circles) {
    let links = [];
    for (let i = 0; i < circles.length; i++) {
        for (let j = 0; j < circles.length; j++) {
            if (i != j) {
                circle1 = circles[i];
                circle2 = circles[j];
                d = get_distance(circle1.x, circle1.y, circle2.x, circle2.y);

                if (d < distance) {
                    links.push(new Link(circle1.x, circle1.y, circle2.x, circle2.y, f(d), canvas))
                }
            }
            

        }
    }

    return links;

}


function get_mouse_links(x, y, circles) {

    let new_links = [];
    for (let i = 0; i < circles.length; i++) {
        
        circle = circles[i];
                
        d = get_distance(circle.x, circle.y, x, y);

        if (d < distance) {
            new_links.push(new Link(circle.x, circle.y, x, y, f(d), canvas))
                }
            }
    

    return new_links;

}


function repulse_circles(x, y, circles) {

    for (let i = 0; i < circles.length; i++) {

        circle = circles[i];
                
        d = get_distance(circle.x, circle.y, x, y);

        if (d < distance) {            
            
            circle.frottement_x = repulsion * (circle.x - x) * (1/d);
            circle.frottement_y = repulsion * (circle.y - y) * (1/d);

                }
            }

    }






class Circle {
    constructor(x0, y0, radius, canvas) {
      this.x = x0;
      this.y = y0;
      this.dx = randint(-vitesse, vitesse);
      this.dy = randint(-vitesse, vitesse);
      this.radius = radius + randint(-2, 2);
      this.canvas = canvas;
      this.context = this.canvas.getContext("2d");
      this.frottement_x = 0;
      this.frottement_y = 0;
      this.shape = SHAPES[Math.round(randint(0, SHAPES.length - 1))];
      this.color = CIRCLE_COLOR;
      
    }

    draw() {

        if (this.shape === 0) {

            this.context.beginPath();
            this.context.fillStyle = "#000000";
            this.context.arc(this.x, this.y, this.radius+0.1, 0, 2 * Math.PI);
            this.context.fill();

            this.context.beginPath();
            this.context.fillStyle = this.color;
            this.context.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
            this.context.fill(); 
        }

        if (this.shape === 1) {

            this.context.beginPath();
            this.context.fillStyle = this.color;
            this.context.arc(this.x, this.y, this.radius+1, 0, 2 * Math.PI);
            this.context.fill();

            this.context.beginPath();
            this.context.fillStyle = BG_COLOR;
            this.context.arc(this.x, this.y, this.radius-0.8, 0, 2 * Math.PI);
            this.context.fill(); 

            this.context.beginPath();
            this.context.fillStyle = this.color;
            this.context.arc(this.x, this.y, this.radius-2, 0, 2 * Math.PI);
            this.context.fill();
        }


    }


    move() {
        this.x += this.dx + this.frottement_x;
        this.y += this.dy + this.frottement_y;

        if (this.x + radius > this.canvas.width || this.x - radius < 0) {
            this.dx = -this.dx;  // Inverser la direction horizontale
        }
    
        if (this.y + radius > this.canvas.height || this.y - radius < 0) {
            this.dy = -this.dy;  // Inverser la direction verticale
        }

        this.frottement_x /= 2;
        this.frottement_y /= 2;

    }

  }

class Link {
    constructor(x0, y0, x1, y1, alpha, canvas) {
        this.x0 = x0;
        this.x1 = x1;
        this.y0 = y0;
        this.y1 = y1;
        this.alpha = alpha;
        this.canvas = canvas;
        this.context = this.canvas.getContext("2d");
        this.color = LINK_COLOR;
    }

    draw() {
        this.context.beginPath();
        //this.context.strokeStyle = 'rgba(0,0,0,' + this.alpha + ')';
        this.context.strokeStyle = 'rgba(' + this.color[0] + ',' + this.color[1] + ',' + this.color[2] + ',' + this.alpha + ')';
        this.context.moveTo(this.x0, this.y0);
        this.context.lineTo(this.x1, this.y1);
        this.context.stroke();
    }
}



// Initialize variables
let canvas = document.getElementById("canvas2");
let circles = [];

// Create circles
for (let i = 0; i < n_circles; i++) {
    let new_circle = new Circle(randint(radius, canvas.width - radius), randint(radius, canvas.height - radius), radius, canvas);
    circles.push(new_circle);
}

let links = get_links(circles);



function loop() {
    var canvas = document.getElementById("canvas2");
    canvas.addEventListener('mousemove', function(event) {
        var rect = canvas.getBoundingClientRect();
        mouseX = event.clientX - rect.left;
        mouseY = event.clientY - rect.top;
    });
    var context = canvas.getContext("2d");

    context.fillStyle = BG_COLOR;
    context.fillRect(0, 0, canvas.width, canvas.height);
    

    // Effacer le canvas
    //context.clearRect(0, 0, canvas.width, canvas.height);

    

    links = get_links(circles);

    if (!isNaN(mouseX )) {
        mouse_links = get_mouse_links(mouseX, mouseY, circles);
        links.push.apply(links, mouse_links);
    }
    
    repulse_circles(mouseX, mouseY, circles);

    
    


    for (let i = 0; i < links.length; i++) {
        links[i].draw();
    }

    for (let i = 0; i < circles.length; i++) {
        circles[i].move();
        circles[i].draw();
    }
    
    

    // Refaire l'animation
    requestAnimationFrame(loop);
}



// Démarrer l'animation
loop();