import processing.video.*;

class camera
{
  Capture cam;

  String[] cameras = Capture.list();

  void checkCameras()
  {
    if (cameras.length == 0)
    {
      print("Missing Camera Input");
    } else {

      print("\nAvailable Cameras: ");
      for (int i = 0; i < cameras.length; i++)
      {
        println(cameras[i]);
      }
    }
  }

  void takePicture()
  {
    if (cam.available() == true)
    {
     cam.read(); 
    }
    
    image(cam, 0, 0);
  }
}
