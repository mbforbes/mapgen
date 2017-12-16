void setup() {
    size(500, 500);
    background(255);
    noLoop();
}

/**
 * Given:
 * - "/foo/bar/baz.txt" (fn)
 * - "/output/"         (out_dir)
 *
 * Returns:
 * - "/output/baz.png"
 */
String getOutFilename(String fn, String out_dir) {
    String[] pieces = split(fn, "/");
    String basename = pieces[pieces.length - 1];
    String preExt = split(basename, ".")[0];
    String middle = "";
    if (out_dir.charAt(out_dir.length() - 1) != '/') {
        middle = "/";
    }
    return out_dir + middle + preExt + ".png";
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

void drawBuilding(int[][] coords) {
    // TODO: stroke
    // TODO: any line thickness?
    // TODO: color
    fill(255, 0, 0);
    stroke(0);
    beginShape();
    for (int i = 0; i < coords.length; i++) {
        vertex(coords[i][0], coords[i][1]);
    }
    endShape(CLOSE);
}

void drawWalkway(int[][] coords) {
    // TODO: stroke
    // TODO: any line thickness?
    // TODO: color
    fill(200);
    stroke(0);
    beginShape();
    for (int i = 0; i < coords.length; i++) {
        vertex(coords[i][0], coords[i][1]);
    }
    endShape(CLOSE);
}

void drawHighway(int[][] coords) {
    // TODO: line thickness
    // TODO: line color
    noFill();
    stroke(0);
    beginShape();
    for (int i = 0; i < coords.length; i++) {
        vertex(coords[i][0], coords[i][1]);
    }
    endShape();
}

void drawWater(int[][] coords) {
    // TODO: stroke
    // TODO: any line thickness?
    // TODO: color
    fill(0, 0, 255);
    stroke(0);
    beginShape();
    for (int i = 0; i < coords.length; i++) {
        vertex(coords[i][0], coords[i][1]);
    }
    endShape(CLOSE);
}


void handleFile(String in_path, String out_path) {
    String[] lines = loadStrings(in_path);
    for (int i = 0; i < lines.length; i++) {
        // extract data
        String[] pieces = split(lines[i], ";");
        String category = pieces[0];
        int[][] coords = str2vertices(pieces[1]);

        // multiplex to drawing method
        if (category.equals("building")) {
            drawBuilding(coords);
        }
        if (category.equals("highway")) {
            drawHighway(coords);
        }
        if (category.equals("water")) {
            drawWater(coords);
        }
        if (category.equals("walkway")) {
            drawWalkway(coords);
        }
    }

    // after all lines drawn, write out
    save(out_path);
}

void draw() {
    // TODO: loop over files here (if needed) and maybe make more handy
    String in_path = "/home/max/repos/mapgen/data/chunks/B/chunk-test-1.txt";
    String out_dir = "/home/max/repos/mapgen/data/chunks/B/";
    String out_path = getOutFilename(in_path, out_dir);

    handleFile(in_path, out_path);

    exit();
}
