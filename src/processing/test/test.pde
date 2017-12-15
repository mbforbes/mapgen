// gen setup
size(250, 250);
background(255);
stroke(255);

// block
fill(128);
beginShape();
vertex(30, 20);
vertex(45, 30);
vertex(80, 20);
vertex(85, 75);
vertex(30, 75);
endShape(CLOSE);

// bldng
fill(0);
beginShape();
vertex(100, 200);
vertex(150, 249);
vertex(75, 75);
endShape(CLOSE);


// write
save("out.png");

