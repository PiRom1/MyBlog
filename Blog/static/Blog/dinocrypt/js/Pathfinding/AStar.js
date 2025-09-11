

class AStar {

    constructor(array) {
        this.array = array;
        this.dirs = Array(Array(0, 1), Array(0, -1), Array(1, 0), Array(-1, 0));
        this.cells = {};
    }

   
    distance(startCell, targetCell) {
        // Manhattan distance
        return Math.abs(targetCell.coords[0] - startCell.coords[0]) +
               Math.abs(targetCell.coords[1] - startCell.coords[1]);
    }


    getAdjacentCells(cell) {
        //
        // Get all free cells around the current cell
        //

        let adjacent_cells = Array();
        this.dirs.forEach(dir => {

            const newX = cell.x + dir[0];
            const newY = cell.y + dir[1];

            // Check if newX and newY are in the array
            if ( (newX >= 0 && newX < this.array.length && newY >= 0 && newY < this.array[0].length)) { 

                // Check if the new cell is free
                if (this.array[newY][newX] === 1) {
                    // Check if the new cell is not in taken cells:
                    if (!this.taken_cells.includes(`${newX}_${newY}`)) {
                        adjacent_cells.push({"x" : newX, "y" : newY, "distance" : cell.currentDistance + 1, "parent" : cell});
                    }

                }
            }
        })

        return adjacent_cells;

    }



    getHeuristicDistance(cell, target_cell) {
        `
        Manhattan distance between 2 cells
        `
        const dist = Math.abs(target_cell.x - cell.x) + Math.abs(target_cell.y - cell.y);
        return dist;

    }




    getCurrentCell() {

        let distances = [];

        this.cellsToExplore.forEach(cell => {
            let distance = cell.currentDistance + cell.heuristicDistance;
            distances.push(distance);
        })


        let index_min_distance = distances.indexOf(Math.min(...distances));

        return this.cellsToExplore[index_min_distance];

    }


    updateExploration(current_cell, adjacent_cells) {
        //
        // Update the cellsToExplore and exploredCells arrays
        //

        adjacent_cells.forEach(cell => {
         
            // Si la cellule n'avais pas encore été déclarée, la déclarer + l'ajouter à 'to_explore'
            if (!(`${cell.x}_${cell.y}` in this.cells)) {
                let new_cell = new Cell(cell["x"], cell["y"], cell["distance"], this.getHeuristicDistance(cell, this.targetCell), cell["parent"]);
                this.cells[`${cell.x}_${cell.y}`] = new_cell;
                this.cellsToExplore.push(new_cell)
            }

            // Sinon, soit elle a été explorée soit elle est déjà dans to explore. Donc rien

        })

        this.exploredCells.push(current_cell);
        this.cellsToExplore = this.cellsToExplore.filter(c => c.x !== current_cell.x || c.y !== current_cell.y);

    

    }


    aStar(start_x, start_y, target_x, target_y, taken_cells) {

        // Init
        this.startCell = new Cell(start_x, start_y, 0, 0, null);
        this.targetCell = new Cell(target_x, target_y, 0, 0, null);
        this.taken_cells = taken_cells;

        console.log(`A Star initialisation from ${this.startCell.toString()} to ${this.targetCell.toString()} ... `);
        this.cells = {};
        this.cellsToExplore = Array();
        this.exploredCells = Array();
        
        let adjacent_cells = this.getAdjacentCells(this.startCell);
        this.updateExploration(this.startCell, adjacent_cells);


        let n = 1;
        while (true) {
            const current_cell = this.getCurrentCell();
            if (!current_cell) { // Si pas de chemin optimal
                return;
            }

            // Target found
            if (current_cell.y === this.targetCell.y &&
                current_cell.x === this.targetCell.x) {
                this.targetCell = current_cell;
                break;
            }

            
            // Explore neighbors
            let adjacent_cells = this.getAdjacentCells(current_cell);
            if (adjacent_cells.length === 0) {
                break;
            } 
            this.updateExploration(current_cell, adjacent_cells);

          
            n++;


            if (n > 2000) {
                break;
            }
        }

        // Reconstruct path
        let cell = this.targetCell;
        const path = [];
        while (cell) {
            path.push([cell.x, cell.y]);
            cell = cell.parent;
        }

        return path.reverse();
    }
}