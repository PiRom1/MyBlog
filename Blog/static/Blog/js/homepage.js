

document.addEventListener('DOMContentLoaded', function () {
   
    const main_circle = document.getElementById('main_circle');
    const nb_categories = 5;
    const data = document.getElementById('data');
    const categories = JSON.parse(data.getAttribute('categories'));
    const subcategories = document.getElementById('subcategories');
    let last_colored;
    let small_circles = [];


    
    function position_small_circles() {
        const circle_rect = main_circle.getBoundingClientRect();

        const circle_x = circle_rect.left + circle_rect.width / 2;
        const circle_y = circle_rect.top + circle_rect.height / 2;
        const circle_radius = main_circle.offsetWidth / 2;

        small_circles.forEach((circle, i) => {
            let angle = ((2 * Math.PI) / nb_categories) * i - Math.PI / 2;

            let new_x = circle_x + Math.cos(angle) * circle_radius;
            let new_y = circle_y + Math.sin(angle) * circle_radius;

            circle.style.left = new_x + 'px';
            circle.style.top  = new_y + 'px';
        });
    }




    function color_small_circle() {
        small_circles.forEach(circle => {
            circle.style.backgroundColor = "rgb(212, 145, 145)";
            circle.style.boxShadow = "";
            circle.style.width = "12vmin";
            circle.style.height = "12vmin";
        })
        last_colored.style.backgroundColor = "rgb(227, 187, 187)";
        last_colored.style.boxShadow = "0 0 10px rgba(175, 93, 93, 0.8), 0 0 25px rgba(180, 95, 95, 0.6), 0 0 50px rgba(156, 84, 84, 0.4)";
        last_colored.style.width = "13vmin";
        last_colored.style.height = "13vmin";
    }
    



    function add_subcategories(circle_subcategories) {
        subcategories.innerHTML = "";
        circle_subcategories.forEach(circle_subcategory => {
            let text_subcategory = document.createElement('a');
            text_subcategory.innerHTML = `${circle_subcategory['name']}<br>`
            text_subcategory.href = circle_subcategory['link'];
            text_subcategory.style.textDecoration = 'none';
            text_subcategory.style.color = 'inherit';
            text_subcategory.classList.add("subcategory");
            subcategories.appendChild(text_subcategory);

          
            
        })
        console.log(subcategories);
    }



    function add_categories() {
        for (let i = 0; i < nb_categories; i++) {

            let new_circle = document.createElement('div');
            new_circle.classList.add("small_circle");

            new_circle.innerHTML = categories[i]['category'];

            document.body.appendChild(new_circle);

            new_circle.addEventListener('mouseover', function() {
                circle_subcategories = categories[i]['subcategory'];
                add_subcategories(circle_subcategories);
                last_colored = new_circle;
                color_small_circle();
            });

            small_circles.push(new_circle);
        }

        // Position initiale
        position_small_circles();
    }

    window.addEventListener('resize', position_small_circles);



    add_categories();

});
