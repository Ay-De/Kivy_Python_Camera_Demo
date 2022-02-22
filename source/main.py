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
from itertools import cycle

#from jnius import autoclass

# Check if platform is android and import permissions for the popup
if (platform == 'android'):
    from android.storage import primary_external_storage_path
    import permissions

class MainPage(Image, Screen):

   # if (platform == 'android') and (platform == 'windows'):
   #     Camera = autoclass('android.hardware.Camera')
   #     try:
   #         co = Camera.open(int(0))
   #         x = co.getParameters().getSupportedPictureSizes()
   #         print(x)
   #         co.release()
   #     except:
   #         print('could not open camera')

    def __init__(self, index2=0, **kwargs):
        super(MainPage, self).__init__(**kwargs)
        print('index2 in init:', index2)
        self.reset(index2)

    def reset(self, index2):
        print('index2 in reset:', index2)
        # Index of camera to use
        self.index = index2
        # Framerate per seconds at which the images should be drawn again
        self.fps = 30

        self.rawHeight = 10000
        self.rawWidth = 10000

        self.codec = 859981650  # FourCC Codec to use, here RGB3

        self.jpegQuality = 100  # in %
        self.previewHeight = 960
        self.previewWidth = 1280

        self.texture = Texture.create(size=(self.previewWidth, self.previewHeight), colorfmt='rgb')
        self.lenses = []

        # Get number of cameras
        for n in range(0, 5):
            self._tempCam = cv2.VideoCapture(n, cv2.CAP_DSHOW) if (platform == 'win') else cv2.VideoCapture(n,
                                                                                                            cv2.CAP_ANDROID)

            if self._tempCam.isOpened():
                self.lenses.append(n)
                self._tempCam.release()

            else:
                self._tempCam.release()
                break

        print(self.lenses)
        self.cyclelens = cycle(self.lenses)

        # Connect CV2 to camera
        if (platform == 'android'):
            self.imageStreamFromCamera = cv2.VideoCapture(self.index, cv2.CAP_ANDROID)
            self.downloadDir = os.path.join(primary_external_storage_path(), 'Download')
        else:
            self.downloadDir = str(Path.home() / 'Downloads')
            self.imageStreamFromCamera = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
            # self.imageStreamFromCamera.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        if self.imageStreamFromCamera.isOpened():
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FRAME_WIDTH, self.rawWidth)
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.rawHeight)
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FOURCC, self.codec)
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FPS, self.fps)

        # Clock will call a function in a specified interval in seconds
        Clock.schedule_interval(self._drawImage, (1.0 / self.fps))

   #Note: dt is not used, but required by kivys Clock.schedule_interval function
    def _drawImage(self, dt):

        #Get image from Camera
        _retval, self.frame = self.imageStreamFromCamera.read()
        if (platform == 'win'):
            self.frame = cv2.flip(self.frame, 0)
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

        self._image = self.frame
        self._timeStamp = time.strftime('%Y%m%d_%H%M%S')

        if platform == 'win':
            self._image = cv2.flip(cv2.cvtColor(self._image, cv2.COLOR_RGB2BGR), 0)
        else:
            self._image = cv2.cvtColor(self._image, cv2.COLOR_RGB2BGR)

        thread = threading.Thread(target=cv2.imwrite,
                                  args=[os.path.join(self.downloadDir, f'IMG_{self._timeStamp}.jpg'),
                                        self._image,
                                        [int(cv2.IMWRITE_JPEG_QUALITY), self.jpegQuality]])
        thread.start()

    def switchLens(self):
        self.imageStreamFromCamera.release()

        #This if statement is required, because next() returns the first element in the list on the first call
        #instead of the next element. Only happens on the first call
        if not hasattr(self, 'activeLens'):
            self.activeLens = next(self.cyclelens)

        self.activeLens = next(self.cyclelens)

        #Reload the Class with the new Camera Lens
        MainPage.reset(self, self.activeLens)

        #self.imageStreamFromCamera = cv2.VideoCapture(next(self.cyclelens), cv2.CAP_ANDROID)
        #self.imageStreamFromCamera.set(cv2.CAP_PROP_FRAME_WIDTH, self.rawWidth)
        #self.imageStreamFromCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.rawHeight)
        #self.width2 = self.imageStreamFromCamera.get(cv2.CAP_PROP_FRAME_WIDTH)
        #self.height2 = self.imageStreamFromCamera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        #print(self.width2, self.height2)
        #self.imageStreamFromCamera.set(cv2.CAP_PROP_FOURCC, self.codec)
        #self.imageStreamFromCamera.set(cv2.CAP_PROP_FPS, self.fps)

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