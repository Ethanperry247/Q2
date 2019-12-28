PImage input;
boolean createMatrix = false;

//SHOULD BE THE SAME AS THE SIZE.
int resolution = 1000;

//Counts the total number of pixels in the image. Equals width*height.
int totalCount = 0;

//Counts the number of white pixels in the image.
int whitePixelCount = 0;

//Restraint of what is considered "white." True white is (255,255,255) and black is (0,0,0).
int whiteRestraint = 200;

PImage[] testCups = new PImage[7];

void setup()
{
  size(1000, 1000);
  //background(0);
  load();
}

void draw()
{
  //Runs checkInput method.
  checkInput(input);

  //Draws image.
  image(input, 0, 0, resolution, resolution);

  //Loads pixels[] matrix.
  loadPixels();

  if (createMatrix == false)
  {
    //checkCups();
  }

  //Accesses pixel information.
  if (createMatrix == false)
  {
    input.loadPixels();

    for (int i = 0; i < width*height; i++)
    {
      color col = pixels[i];



      if (red(col) > whiteRestraint && green(col) > whiteRestraint && blue(col) > whiteRestraint)
      {
        //print (red(col) + " " + green(col) + " " + blue(col) + "    ");
        whitePixelCount++;
      }

      input.updatePixels();

      totalCount++;
    }

    float pixelProp = ((float)whitePixelCount / (float)totalCount)*100;
    print("\n\nTotal Pixels Checked: " + totalCount + "\nWhite Pixels: " + whitePixelCount + "\nProportion: " + pixelProp + "%");
  }

  /*
  for (int i = 0; i < width*height; i++)
  {
    color col = pixels[i];
    if (red(col) > whiteRestraint && green(col) > whiteRestraint && blue(col) > whiteRestraint)
    {
      //print (red(col) + " " + green(col) + " " + blue(col) + "    ");
      colorPink(i);
    }
  }
  */

  //Inhibits pixel access after one loop.
  createMatrix = true;
}

//Loads all images.
void load()
{
  input = loadImage("TestCups/cup7.jpg");
  //input = loadImage("white.png");

/*
  testCups[0] = loadImage("TestCups/cup1.jpg");
  testCups[1] = loadImage("TestCups/cup2.jpg");
  testCups[2] = loadImage("TestCups/cup3.jpg");
  testCups[3] = loadImage("TestCups/cup4.jpg");
  testCups[4] = loadImage("TestCups/cup5.jpg");
  testCups[5] = loadImage("TestCups/cup6.jpg");
  testCups[6] = loadImage("TestCups/cup7.jpg");
  */
}

//Checks for mistakes in the kcup.
boolean checkInput(PImage p)
{
  return false;
}

void colorPink(int i)
{
  loadPixels();
  pixels[i] = color(255, 0, 144);
  updatePixels();
}

void checkCups()
{

  for (int i = 0; i < testCups.length; i++)
  {
    image(testCups[i], 0, 0, resolution, resolution); 

    for (int j = 0; j < width*height; j++)
    {
      color col = pixels[j];

      if (red(col) > whiteRestraint && green(col) > whiteRestraint && blue(col) > whiteRestraint)
      {
        //print (red(col) + " " + green(col) + " " + blue(col) + "    ");
        whitePixelCount++;
      }

      input.updatePixels();

      totalCount++;
    }

    float pixelProp = ((float)whitePixelCount / (float)totalCount)*100;

    int temp = i + 1;
    print("\n\nCup #" + temp + ":\n");
    print("Total Pixels Checked: " + totalCount + "\nWhite Pixels: " + whitePixelCount + "\nProportion: " + pixelProp + "%");
  }
}
