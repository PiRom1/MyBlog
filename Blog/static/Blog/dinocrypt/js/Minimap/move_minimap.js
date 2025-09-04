let is_mousedown = false;

let click_x;
let click_y;
let initial_min_minimap_x;
let initial_max_minimap_x;
let initial_min_minimap_y;
let initial_max_minimap_y;

canvas.addEventListener('mousedown', function(e) {
    console.log(e.clientX - canvas_x, e.clientY - canvas_y);
    click_x = e.clientX - canvas_x;
    click_y = e.clientY - canvas_y;
    

    if (click_x > minimap.x_min_coord && click_x < minimap.x_max_coord) {
        if (click_y > minimap.y_min_coord && click_y < minimap.y_max_coord) {
            is_mousedown = true;
            initial_min_minimap_x = minimap.x_min_coord;
            initial_max_minimap_x = minimap.x_max_coord;
            initial_min_minimap_y = minimap.y_min_coord;
            initial_max_minimap_y = minimap.y_max_coord;
        }
    }

})


document.addEventListener('mouseup', function() {
    is_mousedown = false;
})


canvas.addEventListener('mousemove', function(e) {
    if (is_mousedown) {
        const x = e.clientX - canvas_x;
        const y = e.clientY - canvas_y;
        let offset_x = x - click_x;
        let offset_y = y - click_y;
        minimap.x_min_coord = initial_min_minimap_x + offset_x;
        minimap.x_max_coord = initial_max_minimap_x + offset_x;
        minimap.y_min_coord = initial_min_minimap_y + offset_y;
        minimap.y_max_coord = initial_max_minimap_y + offset_y;
        minimap.actualize();
        
    }
})