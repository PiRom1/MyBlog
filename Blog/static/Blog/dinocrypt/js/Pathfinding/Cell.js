class Cell {

    constructor(x, y, currentDistance, heuristicDistance, parent) {
        
        this.x = x;
        this.y = y;
        this.parent = parent;

        this.currentDistance = currentDistance;
        this.heuristicDistance = heuristicDistance;
    }

    toString() {
        return `Cell(coords=${this.x};${this.y}, currentDistance=${this.currentDistance}, heuristicDistance=${this.heuristicDistance})`;
    }

}