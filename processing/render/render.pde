// setup has to be up-top, i think
void setup() {
    size(250, 250);
    background(255);
    noLoop();
}

int[][] str2vertices(String line) {
    String[] pieces = split(line, " ");

    int[][] result = new int[pieces.length][2];

    for (int i = 0; i < pieces.length; i++) {
        int[] coords = int(split(pieces[i], ","));
        result[i][0] = coords[0];
        result[i][1] = coords[1];
    }

    return result;
}

void drawBlock(int[][] block) {
    fill(128);
    stroke(128);
    beginShape();
    for (int i = 0; i < block.length; i++) {
        vertex(block[i][0], block[i][1]);
    }
    endShape(CLOSE);
}

void drawBuilding(int[][] building) {
    fill(0);
    stroke(0);
    beginShape();
    for (int i = 0; i < building.length; i++) {
        vertex(building[i][0], building[i][1]);
    }
    endShape(CLOSE);
}

// handles a single input file
void handleFile(String fn, String out_fn) {
    // TODO: beginDraw(), endDraw(), and clear() may be useful for saving
    // multiple files.

    String[] lines = loadStrings(fn);
    drawBlock(str2vertices(lines[0]));

    for (int i = 1; i < lines.length; i++) {
        drawBuilding(str2vertices(lines[i]));
    }

    save(out_fn);
}

void draw() {
    handleFile("/home/max/repos/mapgen/data/fbs/north-winds-0.txt", "temp.png");
}

