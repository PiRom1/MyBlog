
//// Create canva


const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

console.log("canvas : ", canvas);

// Ajuster la résolution du canvas à la taille d'affichage :
canvas.width = canvas.clientWidth;
canvas.height = canvas.clientHeight;

//// Get parameters

const TILES_PER_ROW = 35;
const TILES_PER_COLUMN = 15;
const TILE_WIDTH = canvas.width / TILES_PER_ROW;
const TILE_HEIGHT = canvas.height / TILES_PER_COLUMN;

const MOVE_THRESHOLD = 0.4;
const MOVE_THRESHOLD_X = MOVE_THRESHOLD * TILES_PER_ROW;
const MOVE_THRESHOLD_y = MOVE_THRESHOLD * TILES_PER_COLUMN;

const NB_MOVING_FRAMES = 5; // Nb frames for one deplacement



// Useful functions

// Returns a random real number between min and max
function large_random(min, max) {
    return min + (max - min) * Math.random();
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


