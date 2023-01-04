
# CamBuddy

CamBuddy takes time-lapse images of your plants.

- inexpensive, uses ESP32 AI Thinker Cam.
- lots of coding examples, people using it for this.
- easy.  images are saved and processed on gus into a video stream that can be uploaded to YouTube.
- images are archived and prepped for preprocessing into a deep learning model.
- simple.  Does one thing. Timelapse.
- can set the start time, end time, time between snapshots, filename, where to save the video (default Gus, could be YouTube?)

## Code
- ESP32 - FTDI to plug into PC?... i have this old one lying around...take pic, put link when get to making materials list.
- get Arduino code running.
    - see [random nerd's Installing the ESP32 Board in Arduino IDE tutorial](https://randomnerdtutorials.com/installing-the-esp32-board-in-arduino-ide-windows-instructions/).
this gets us to the esp32

### USB -> FTDI -> ESP32
Unfortunately, the AI Thinker ESP32 does not have a USB connector.  We need to convert the RS232 Serial speak into the USB speak our computer understand. To do this, we need
an FTDI USB to Serial adapter board like [this one](https://amzn.to/3CfLb5A).
#### Set Up Windows Drivers
 Assuming you are on a Windows 10 PC (I say this because it is what I am running),  follow the steps outlined in
[Darren Robinson's article, ESP32 Com Port – CP2102 USB to UART Bridge Controller](https://blog.darrenjrobinson.com/esp32-com-port-cp2102-usb-to-uart-bridge-controller/).
#### Connect the FTDI adapter board
Here's the FTDI adapter board I used.  There are many different boards available.  The setup should be the same.
:::{figure} images/ftdiSerialToUSB.jpeg
:align: center
:scale: 50

FTDI Adapter Board
:::
The Arduino IDE should now be able to recognize a COM port.
The following wires need to be connected:
:::{figure} images/esp32camtoftdi.jpg
:align: center
:scale: 50

From [How to Upload Coad to ESP32-CAM](https://embedgyan.wordpress.com/2020/06/10/how-to-program-upload-code-to-esp32-cam-ai-thinker-arduino-ide/)
:::
To upload the code to the ESP32 Cam, you will need to connect the GPIO0 pin to GND. This will put the device into flashing mode, allowing you to write the code to the ESP32 Cam.
#### Uploading Code
Time to upload some `.ino` file.  The thing to keep in mind is getting the ESP32Cam in and out of the ability to upload code versus running code.  To upload code:
- Make sure the GPIO 0 pin is tied down to GND.
- Hit the RST button.
- The code should upload at the point
#### Running code
- Disconnect the GPIOP0 to GND wire (this takes the ESP32Cam out of Flashing (i.e.: code uploading) mode).
- Hit the RST button.
- If the code has `Serial.println()` statements, these should show up in the Serial Monitor.
### Image Size and Format
I asked chatGPT, _What image size and format is typically used as input into a CNN?_


The response: _Some common image sizes for use in CNNs include 256x256, 224x224, and 227x227 pixels. These sizes are small enough to allow the model to process the images efficiently, while still providing sufficient resolution for the CNN to extract useful features from the images. In terms of image format, it is generally best to use image files in a lossless format, such as PNG or TIFF, when training a CNN. These formats allow you to preserve the original quality of the images, which is important for maintaining the integrity of the data_

Based on this insight, images will be stored on Gus with a size of 256 x 256 and in png format.

The camera on the AI Thinker is the OV2640.  The supported image formats are:
PIXFORMAT_YUV422
PIXFORMAT_GRAYSCALE
PIXFORMAT_RGB565
PIXFORMAT_JPEG

Since png is not one of the choice, we will use JPEG as the image format.

The frame size can be set to one of:
FRAMESIZE_UXGA (1600 x 1200)
FRAMESIZE_QVGA (320 x 240)
FRAMESIZE_CIF (352 x 288)
FRAMESIZE_VGA (640 x 480)
FRAMESIZE_SVGA (800 x 600)
FRAMESIZE_XGA (1024 x 768)
FRAMESIZE_SXGA (1280 x 1024)

The closest fit is FRAMESIZE_QVGA

initCamera.cpp and initCamera.h are all the parameters and initialization of the camera.

setup

- enable brownout detection.... doc see -= https://iotespresso.com/how-to-disable-brownout-detector-in-esp32-in-arduino/
The soc.h file contains the WRITE_PERI_REG() function, and the rtc_cntl_reg.h contains the RTC_CNTL_BROWN_OUT_REG register.

I am using the settings for the AI Thinker ESP32-CAM.  One thing that we might want to change is the image quality or perhaps the pixel format.  The constants are defined in [espressif's esp32-camera file sensor.h](https://github.com/espressif/esp32-camera/blob/master/driver/include/sensor.h).

FTP on Arduino requires installing [esp32_ftpclient](https://www.arduino.cc/reference/en/libraries/esp32_ftpclient/).  Clicking on the documentation link leads to [here](https://github.com/ldab/ESP32_FTPClient) - a github.