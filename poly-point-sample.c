// FRom;
// http://alienryderflex.com/polygon/
//
//  Globals which should be set before calling this function:
//
//  int    polyCorners  =  how many corners the polygon has (no repeats)
//  float  polyX[]      =  horizontal coordinates of corners
//  float  polyY[]      =  vertical coordinates of corners
//  float  x, y         =  point to be tested
//
//  (Globals are used in this example for purposes of speed.  Change as
//  desired.)
//
//  The function will return YES if the point x,y is inside the polygon, or
//  NO if it is not.  If the point is exactly on the edge of the polygon,
//  then the function may return YES or NO.
//
//  Note that division by zero is avoided because the division is protected
//  by the "if" clause which surrounds it.

bool pointInPolygon() {
    int i;
    // j begins as the final vertex, and then in each iteration, is set to be
    // the previous vertex (i - 1). this is to handle wrapping around
    int j = polyCorners - 1;
    bool oddNodes = false;

    // loop over each vertex
    for (i = 0; i < polyCorners; i++) {


        if (polyY[i] < y && polyY[j] >= y || polyY[j] < y && polyY[i] >= y) {
            if (polyX[i] + (y - polyY[i]) / (polyY[j] - polyY[i]) * (polyX[j] - polyX[i]) < x) {
                oddNodes=!oddNodes;
            }
        }
        j=i;
    }

  return oddNodes;
}
