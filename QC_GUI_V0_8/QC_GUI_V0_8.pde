import processing.serial.*;
import processing.io.*;

//Temp boolean flipper that simulates a good cup passing.
boolean temp = false;

//Serial input
serialInput laserIn;
serialInput boxLoaded;

//Color Scheme:
color orange = color(255, 101, 47);
color yellow = color(255, 228, 1);
color green = color(19, 167, 107);
color black = color(39, 39, 39);
color gray = color(116, 116, 116);
color white = color(245, 245, 245);

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

//GPIO
SoftwareServo servo;
SoftwareServo servo2;


void setup()
{
  fullScreen(P2D);
  background(black);

  //Direct GPIO
  servo = new SoftwareServo(this);
  servo.attach(4);
  servo = new SoftwareServo(this);
  servo.attach(17);
  GPIO.pinMode(18, GPIO.INPUT);

  //laserIn = new serialInput(new Serial(this, Serial.list()[0], 9600));
}

void draw()
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

void mouseClicked()
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

void state(Button state)
{
  if (state.getState())
    state.changeState();
}

void checkCount()
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

void checkState(Button button, color f, color t, String fS, String tS)
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

void boxFill()
{
  if (boxCount >= boxTotal)
  {
    totalBoxes++;
    boxCount = 0;
  }
  
  if (checkLaserInput() && temp == false)
  {
    boxCount++;
    temp = true;
  }
  if (!checkLaserInput() && temp == true)
  {
   temp = false; 
  }
  
  if (keyPressed && key == 'a')
  { 
    boxCount++;
  }
}

//Checks for laser input and returns a true or false.
boolean checkLaserInput() {
  if (GPIO.digitalRead(18) != GPIO.HIGH) {
   return true; 
  } else return false;
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

  boolean checkPort()
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

  void incrementCount()
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
  color textCol; //Color of the text.
  int locX; //X location of the top left corner of the button.
  int locY; //Y location of the top left corner of the button.
  int sizeX; //X size of the button.
  int sizeY; //Y size of the button.
  String text; //Text within the button.
  String outsideText;
  int textSize; //Size of the text within the button.
  int loop = 0;

  Editor(color textCol, int locX, int locY, int sizeX, int sizeY, String text, int textSize, String outsideText)
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

  void display()
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
  color textCol;
  String text;
  int textSize;
  int locX;
  int locY;

  Counter(color t, String text, int textSize, int x, int y)
  {
    textCol = t;
    this.text = text;
    this.textSize = textSize;
    locX = x;
    locY = y;
  }

  void display()
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
  color col; //Color of the button.
  color textCol; //Color of the text within the button.
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
  Button(color col, color textCol, int locX, int locY, int sizeX, int sizeY, String text, int textSize, boolean state)
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

  void drawButton()
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
    text(text, locX + (sizeX)/2, locY + (sizeY)/1.75);
    popMatrix();
  }

  boolean returnState()
  {
    if (mouseX > locX && mouseX < locX + sizeX && mouseY > locY && mouseY < locY + sizeY)
      return true;
    else return false;
  }

  void changeState()
  {
    state = !state;
  }

  boolean getState()
  {
    return state;
  }

  void changeColor(color col)
  {
    this.col = col;
  }

  void changeText(String text)
  {
    this.text = text;
  }
}
