from kivy.utils import platform
from kivy.app import App
from kivy.uix.image import Image
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import Screen, ScreenManager
import threading
from kivy.properties import ObjectProperty
import cv2
import time
import numpy as np
import os
from pathlib import Path

#from jnius import autoclass

print(cv2.__version__)

# Check if platform is android and import permissions for the popup
if (platform == 'android'):
    from android.storage import primary_external_storage_path
    import permissions

class MainPage(Image, Screen):

    #Index of camera to use
    index = 0
    #Framerate per seconds at which the images should be drawn again
    fps = 30

    if (platform == 'android'):
        rawHeight = 3024
        rawWidth = 4032
    else:
        rawHeight = 640
        rawWidth = 480

    codec = 859981650 # FourCC Codec to use, here RGB3

    jpegQuality = 100 #in %
    previewHeight = 1280
    previewWidth = 960

   # if (platform == 'android') and (platform == 'windows'):
   #     Camera = autoclass('android.hardware.Camera')
   #     try:
   #         co = Camera.open(int(0))
   #         x = co.getParameters().getSupportedPictureSizes()
   #         print(x)
   #         co.release()
   #     except:
   #         print('could not open camera')

    def __init__(self, **kwargs):
        super(MainPage, self).__init__(**kwargs)

        self.texture = Texture.create(size=(self.previewWidth, self.previewHeight), colorfmt='rgb')

        #Connect CV2 to camera
        if (platform == 'android'):
            self.imageStreamFromCamera = cv2.VideoCapture(self.index, cv2.CAP_ANDROID)
            self.downloadDir = os.path.join(primary_external_storage_path(), 'Download')
        else:
            self.downloadDir = str(Path.home() / 'Downloads')
            self.imageStreamFromCamera = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
            #self.imageStreamFromCamera.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        if self.imageStreamFromCamera.isOpened():
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.rawHeight)
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FRAME_WIDTH, self.rawWidth)
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FOURCC, self.codec)
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FPS, self.fps)

        #Clock will call a function in a specified interval in seconds
        Clock.schedule_interval(self._drawImage, (1.0/self.fps))

    #Note: dt is not used, but required by kivys Clock.schedule_interval function
    def _drawImage(self, dt):
        #Get image from Camera
        _retval, self.frame = self.imageStreamFromCamera.read()
        if (platform == 'win'):
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)

        #Check if any frame was returned and if yes, process and display it
        if _retval:
         #   if (platform == 'android'):
         #       self.frame = cv2.flip(self.frame, 1)
         #   else:
         #       self.frame = cv2.flip(self.frame, 0)

            self.previewImage = cv2.resize(self.frame,
                                           dsize=(self.previewWidth, self.previewHeight),
                                           interpolation=cv2.INTER_AREA)

            #Update the texture to display the actual image
            self.texture.blit_buffer(self.previewImage.tostring(), colorfmt='rgb', bufferfmt='ubyte')
            self.canvas.ask_update()

    def captureImage(self):

        _image = self.frame
        _timeStamp = time.strftime('%Y%m%d_%H%M%S')

        _image = cv2.cvtColor(_image, cv2.COLOR_RGB2BGR)


        thread = threading.Thread(target=cv2.imwrite,
                                  args=[os.path.join(self.downloadDir, f'IMG_{_timeStamp}.jpg'),
                                        _image,
                                        [int(cv2.IMWRITE_JPEG_QUALITY), self.jpegQuality]])
        thread.start()


class SettingsPage(Screen):
    pass

class WindowManager(ScreenManager):
    pass

class DemoApp(App):
    def build(self):
        kv = Builder.load_file('layout.kv')
        return kv

if __name__ == '__main__':
    DemoApp().run()