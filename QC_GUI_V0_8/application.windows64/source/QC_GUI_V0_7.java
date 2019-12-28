import processing.core.*; 
import processing.data.*; 
import processing.event.*; 
import processing.opengl.*; 

import processing.serial.*; 

import java.util.HashMap; 
import java.util.ArrayList; 
import java.io.File; 
import java.io.BufferedReader; 
import java.io.PrintWriter; 
import java.io.InputStream; 
import java.io.OutputStream; 
import java.io.IOException; 

public class QC_GUI_V0_7 extends PApplet {



//Temp boolean flipper that simulates a good cup passing.
boolean temp = false;

//Serial input
serialInput laserIn;
serialInput boxLoaded;

//Color Scheme:
int orange = color(255, 101, 47);
int yellow = color(255, 228, 1);
int green = color(19, 167, 107);
int black = color(39, 39, 39);
int gray = color(116, 116, 116);
int white = color(245, 245, 245);

//Counters for KCups and Boxes
int boxTotal = 0;
int boxCount = 0;
int totalBoxes = 0;
int goodCups = 0;
int badCups = 0;

//Buttons
Button state = new Button(orange, white, 10, 10, 100, 70, "Off", 32, false);
Button count16 = new Button(yellow, black, 10, 100, 200, 70, "16 Count", 32, false);
Button count24 = new Button(yellow, black, 10, 200, 200, 70, "24 Count", 32, true);
Button count40 = new Button(yellow, black, 10, 300, 200, 70, "40 Count", 32, false);
Button count96 = new Button(yellow, black, 10, 400, 200, 70, "96 Count", 32, false);

//Counters
Counter currentCupCount;
Counter totalBoxCount;
Counter goodCupCount;
Counter badCupCount;


public void setup()
{
  
  background(black);

  //laserIn = new serialInput(new Serial(this, Serial.list()[0], 9600));
}

public void draw()
{
  background(black);
  state.drawButton();
  count16.drawButton();
  count24.drawButton();
  count40.drawButton();
  count96.drawButton();

  checkState(state, green, orange, "On", "Off");
  checkState(count16, gray, yellow, "16 Count", "16 Count");
  checkState(count24, gray, yellow, "24 Count", "24 Count");
  checkState(count40, gray, yellow, "40 Count", "40 Count");
  checkState(count96, gray, yellow, "96 Count", "96 Count");

  currentCupCount = new Counter(white, "Cups in Current Box: " + boxCount, 64, 3*width/4, height/10);
  totalBoxCount = new Counter(white, "Total Boxes Packed: " + totalBoxes, 64, 3*width/4, 2*height/10);
  goodCupCount = new Counter(white, "Total Good Cups: " + goodCups, 64, 3*width/4, 3*height/10);
  badCupCount = new Counter(white, "Total Bad Cups: " + badCups, 64, 3*width/4, 4*height/10);


  currentCupCount.display();
  totalBoxCount.display();
  goodCupCount.display();
  badCupCount.display();

  checkCount();
  
  //laserIn.incrementCount();

  if (state.getState())
  {
    boxFill();
  }
}

public void mouseClicked()
{
  if (state.returnState())
    state.changeState();
  if (count16.returnState())
  {
    count16.changeState();
    state(count24);
    state(count40);
    state(count96);
  }
  if (count24.returnState())
  {
    count24.changeState();
    state(count16);
    state(count40);
    state(count96);
  }
  if (count40.returnState())
  {
    count40.changeState();
    state(count16);
    state(count24);
    state(count96);
  }
  if (count96.returnState())
  {
    count96.changeState();
    state(count16);
    state(count24);
    state(count40);
  }
}

public void state(Button state)
{
  if (state.getState())
    state.changeState();
}

public void checkCount()
{
  if (count16.getState())
    boxTotal = 16;
  if (count24.getState())
    boxTotal = 24;
  if (count40.getState())
    boxTotal = 40;
  if (count96.getState())
    boxTotal = 96;
}

public void checkState(Button button, int f, int t, String fS, String tS)
{
  if (button.getState())
  {
    button.changeColor(f);
    button.changeText(fS);
  } else 
  {
    button.changeColor(t); 
    button.changeText(tS);
  }
}

public void boxFill()
{
  if (boxCount >= boxTotal)
  {
    totalBoxes++;
    boxCount = 0;
  }
  
  if (keyPressed && temp == false)
  {
    boxCount++;
    temp = true;
  }
  if (!keyPressed && temp == true)
  {
   temp = false; 
  }
  
  if (keyPressed && key == 'a')
  { 
    boxCount++;
  }
}



class serialInput
{
  //Serial Data
  Serial myPort;
  String check;
  boolean result = false;
  boolean flipPort = false;

  serialInput(Serial myPort)
  {
    this.myPort = myPort;
  }

  public boolean checkPort()
  {
    if ( myPort.available() > 0) 
    {  // If data is available,
      check = myPort.readStringUntil('\n');
      if (check != null)
      {
        if (check.contains("true") && state.getState())
          result = true;
        else result = false;
      }
    }

    return result;
  }

  public void incrementCount()
  {
    if (checkPort() == true)
    {
      flipPort = true;
    }

    if (checkPort() == false && flipPort == true)
    {
      boxCount++;
      flipPort = false;
    }
  }
}

class Editor
{
  int textCol; //Color of the text.
  int locX; //X location of the top left corner of the button.
  int locY; //Y location of the top left corner of the button.
  int sizeX; //X size of the button.
  int sizeY; //Y size of the button.
  String text; //Text within the button.
  String outsideText;
  int textSize; //Size of the text within the button.
  int loop = 0;

  Editor(int textCol, int locX, int locY, int sizeX, int sizeY, String text, int textSize, String outsideText)
  {
    this.textCol = textCol;
    this.locX = locX;
    this.locY = locY;
    this.sizeX = sizeX;
    this.sizeY = sizeY;
    this.text = text;
    this.textSize = textSize;
    this.outsideText = outsideText;
  }

  public void display()
  {
    pushMatrix();
    textSize(textSize);
    fill(textCol);
    textAlign(CENTER, BASELINE);
    textMode(MODEL);
    text(text, locX, locY);
    popMatrix();

    loop++;
    if (loop >= 20)
    {
      loop = 0;
    }
  }
}

//Class which creates a counter object to be drawn to the GUI.
class Counter
{
  int textCol;
  String text;
  int textSize;
  int locX;
  int locY;

  Counter(int t, String text, int textSize, int x, int y)
  {
    textCol = t;
    this.text = text;
    this.textSize = textSize;
    locX = x;
    locY = y;
  }

  public void display()
  {
    pushMatrix();
    textSize(textSize);
    fill(textCol);
    textAlign(CENTER, BASELINE);
    textMode(SHAPE);
    text(text, locX, locY);
    popMatrix();
  }
}


//Class which creates a button object to be drawn to the GUI.
class Button
{
  int col; //Color of the button.
  int textCol; //Color of the text within the button.
  int locX; //X location of the top left corner of the button.
  int locY; //Y location of the top left corner of the button.
  int sizeX; //X size of the button.
  int sizeY; //Y size of the button.
  String text; //Text within the button.
  int textSize; //Size of the text within the button.
  boolean state;

  //Standard button constructor.
  Button(int locX, int locY, String text)
  {
    col = color(gray);
    textCol = color(white);
    this.locX = locX;
    this.locY = locY;
    sizeX = width/6;
    sizeY = height/6;
    this.text = text;
    textSize = 60;
  }

  //Custon button constructor.
  Button(int col, int textCol, int locX, int locY, int sizeX, int sizeY, String text, int textSize, boolean state)
  {
    this.col = col;
    this.textCol = textCol;
    this.locX = locX;
    this.locY = locY;
    this.sizeX = sizeX;
    this.sizeY = sizeY;
    this.text = text;
    this.textSize = textSize;
    this.state = state;
  }

  public void drawButton()
  {
    pushMatrix();
    fill(col);
    strokeWeight(5);
    if (mouseX > locX && mouseX < locX + sizeX && mouseY > locY && mouseY < locY + sizeY)
      stroke(white);
    else stroke(0);
    rect(locX, locY, sizeX, sizeY);
    popMatrix();

    pushMatrix();
    textSize(textSize);
    fill(textCol);
    textAlign(CENTER, BASELINE);
    textMode(MODEL);
    text(text, locX + (sizeX)/2, locY + (sizeY)/1.75f);
    popMatrix();
  }

  public boolean returnState()
  {
    if (mouseX > locX && mouseX < locX + sizeX && mouseY > locY && mouseY < locY + sizeY)
      return true;
    else return false;
  }

  public void changeState()
  {
    state = !state;
  }

  public boolean getState()
  {
    return state;
  }

  public void changeColor(int col)
  {
    this.col = col;
  }

  public void changeText(String text)
  {
    this.text = text;
  }
}
  public void settings() {  fullScreen(P2D); }
  static public void main(String[] passedArgs) {
    String[] appletArgs = new String[] { "QC_GUI_V0_7" };
    if (passedArgs != null) {
      PApplet.main(concat(appletArgs, passedArgs));
    } else {
      PApplet.main(appletArgs);
    }
  }
}
