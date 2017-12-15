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

// handles a single input file
void handleFile(String fn, String bare_out_dir, String full_out_dir) {
    String[] lines = loadStrings(fn);
    int[][] block = str2vertices(lines[0]);

    // draw the bare version
    clear();
    background(255);
    drawBlock(block);
    save(getOutFilename(fn, bare_out_dir));

    // draw the full version
    clear();
    background(255);
    drawBlock(block);
    for (int i = 1; i < lines.length; i++) {
        drawBuilding(str2vertices(lines[i]));
    }
    save(getOutFilename(fn, full_out_dir));
}

void draw() {
    // settings
    String bare_out_dir = "/home/max/repos/pytorch-CycleGAN-and-pix2pix/datasets/mapgen/A/train/";
    String full_out_dir = "/home/max/repos/pytorch-CycleGAN-and-pix2pix/datasets/mapgen/B/train/";
    String base_name = "/home/max/repos/mapgen/data/fbs/westside-";
    String ext = ".txt";
    int startInclusive = 0;
    int endInclusive = 176;

    // process (no pun intended) each
    for (int i = startInclusive; i <= endInclusive; i++) {
        handleFile(base_name + str(i) + ext, bare_out_dir, full_out_dir);
    }

    exit();
}

