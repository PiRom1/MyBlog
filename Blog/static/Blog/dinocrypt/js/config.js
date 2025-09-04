
//// Create canva
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const canvas_x = canvas.getBoundingClientRect()["x"];
const canvas_y = canvas.getBoundingClientRect()["y"];
const canvas_width = canvas.getBoundingClientRect()["width"];
const canvas_height = canvas.getBoundingClientRect()["height"];

//// Data
const data = document.getElementById('data');
const array = JSON.parse(data.getAttribute("dungeon"));


// Ajuster la résolution du canvas à la taille d'affichage :
canvas.width = canvas.clientWidth;
canvas.height = canvas.clientHeight;

//// Get parameters
let DUNGEON_SIZE = JSON.parse(document.getElementById("data").getAttribute("dungeon_size"));
const TILES_PER_ROW = 35;
const TILES_PER_COLUMN = 15;
const TILE_WIDTH = canvas.width / TILES_PER_ROW;
const TILE_HEIGHT = canvas.height / TILES_PER_COLUMN;

const MOVE_THRESHOLD = 0.4;
const MOVE_THRESHOLD_X = MOVE_THRESHOLD * TILES_PER_ROW;
const MOVE_THRESHOLD_y = MOVE_THRESHOLD * TILES_PER_COLUMN;

const NB_MOVING_FRAMES = 5; // Nb frames for one deplacement

// Minimap parameters
let minimap;

const MINIMAP_X_MIN_COORD = Math.round(canvas.width * 0.70);
const MINIMAP_X_MAX_COORD = Math.round(canvas.width * 0.98);
const MINIMAP_Y_MIN_COORD = Math.round(canvas.height * 0.55);
const MINIMAP_Y_MAX_COORD = Math.round(canvas.height * 0.95);
const MINIMAP_TILE_HEIGHT = (MINIMAP_Y_MAX_COORD - MINIMAP_Y_MIN_COORD) / DUNGEON_SIZE[0];
const MINIMAP_TILE_WIDTH = (MINIMAP_X_MAX_COORD - MINIMAP_X_MIN_COORD) / DUNGEON_SIZE[1];
const MINIMAP_BLINKING_PLAYER_RATE = 40 // Fréquence en frame du clignotement de la tile joueur sur la minimap
const MINIMAP_PLAYER_TILE_COLOR = "#cd1040ff";

console.log(`Minimap : x_min_coord : ${MINIMAP_X_MIN_COORD} / y_min_coord : ${MINIMAP_Y_MIN_COORD}`);
console.log(`Minimap : y_max_coord : ${MINIMAP_X_MAX_COORD} / y_max_coord : ${MINIMAP_Y_MAX_COORD}`);

// 
let lap = 0;


//// Controls
const move_up = ["ArrowUp", "z"];
const move_down = ["ArrowDown", "s"];
const move_left = ["ArrowLeft", "q"];
const move_right = ["ArrowRight", "d"];


// Useful functions

// Returns a random real number between min and max
function large_random(min, max) {
    return min + (max - min) * Math.random();
}

// Compute distance between two points
function distance(x1, y1, x2, y2) {
  return Math.hypot(x2 - x1, y2 - y1);
}


// Returns a random integer number between max and min
function randint(min, max) {
    return Math.floor(min + Math.random() * (max - min));
}

// Generate a random array for the dungeon
function generateRandomArray(rows, columns) {
    let arr = [];

    for (let i = 0; i < rows; i++) {
        arr[i] = [];

        for (let j = 0; j < columns; j++) {
            if (i === 0 || j === 0 || i === rows - 1 || j === columns - 1) {
                arr[i][j] = 0;
            } else {
                arr[i][j] = Math.random() < 0.5 ? 0 : 1;
            }
        }
    }
    return arr;
}


