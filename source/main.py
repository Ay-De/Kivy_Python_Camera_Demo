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


class Settings:

    jpegQuality = 98


class MainPage(Image, Screen, Settings):

   # if (platform == 'android') and (platform == 'windows'):
   #     Camera = autoclass('android.hardware.Camera')
   #     try:
   #         co = Camera.open(int(0))
   #         x = co.getParameters().getSupportedPictureSizes()
   #         print(x)
   #         co.release()
   #     except:
   #         print('could not open camera')

    def __init__(self, nextLens=0, **kwargs):
        super(MainPage, self).__init__(**kwargs)

        # Framerate per seconds at which the images should be drawn again
        self.fps = 30

        # Setting raw sensor height and width to 10000, to get the highest possible resolution.
        self.rawHeight = 10000
        self.rawWidth = 10000

        #self.jpegQuality = 100  # in %

        if platform == 'win':
            self.previewHeight = 960
            self.previewWidth = 1280
        else:
            self.previewHeight = 1280
            self.previewWidth = 960

        self.texture = Texture.create(size=(self.previewWidth, self.previewHeight), colorfmt='rgb')

        self.lenses = []

        # Get number of cameras
        for n in range(0, 5):
            self._tempCam = cv2.VideoCapture(n,
                                             cv2.CAP_DSHOW) if (platform == 'win') else cv2.VideoCapture(n,
                                                                                                            cv2.CAP_ANDROID)

            if self._tempCam.isOpened():
                self.lenses.append(n)
                self._tempCam.release()

            else:
                self._tempCam.release()
                break

        self.cyclelens = cycle(self.lenses)

        print(self.lenses)


        self._switch(nextLens)

    def _switch(self, nextLens):
        print('nextLens in reset:', nextLens)
        # Index of camera to use
        self.index = nextLens

        while (nextLens != next(self.cyclelens)):
            next(self.cyclelens)
            print(next(self.cyclelens))

        # Connect CV2 to camera
        if (platform == 'android'):
            self.imageStreamFromCamera = cv2.VideoCapture(self.index, cv2.CAP_ANDROID)
            self.downloadDir = os.path.join(primary_external_storage_path(), 'Download')
        else:
            self.downloadDir = str(Path.home() / 'Downloads')
            self.imageStreamFromCamera = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)


        if self.imageStreamFromCamera.isOpened():
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FRAME_WIDTH, self.rawWidth)
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.rawHeight)
            print('height', self.imageStreamFromCamera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print('width', self.imageStreamFromCamera.get(cv2.CAP_PROP_FRAME_WIDTH))

            self.imageStreamFromCamera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('R','G','B','3'))
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FPS, self.fps)
            self.imageStreamFromCamera.set(cv2.CAP_PROP_BUFFERSIZE, 3)

        # Clock will call a function in a specified interval in seconds
        Clock.schedule_interval(self._drawImage, (1.0 / self.fps))

   #Note: dt is not used, but required by kivys Clock.schedule_interval function
    def _drawImage(self, dt):

        #Get image from Camera
        _retval, self.frame = self.imageStreamFromCamera.read()
        if (platform == 'win'):
            self.frame = cv2.flip(self.frame, 0)
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
        else:
            self.frame = cv2.flip(self.frame, 0)
            self.frame = cv2.rotate(self.frame, cv2.ROTATE_90_CLOCKWISE)
            self.frame = cv2.flip(self.frame, 1)
            #self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)

        #Check if any frame was returned and if yes, process and display it
        if _retval:
         #   if (platform == 'android'):
         #       self.frame = cv2.flip(self.frame, 1)
         #   else:
         #       self.frame = cv2.flip(self.frame, 0)

            self.previewImage = cv2.resize(self.frame,
                                           dsize=(self.previewWidth, self.previewHeight),
                                           interpolation=cv2.INTER_NEAREST)

            #Update the texture to display the actual image
            self.texture.blit_buffer(self.previewImage.tostring(), colorfmt='rgb', bufferfmt='ubyte')
            self.canvas.ask_update()

    def captureImage(self):

        self._image = self.frame
        self._timeStamp = time.strftime('%Y%m%d_%H%M%S')

        if platform == 'win':
            self._image = cv2.flip(cv2.cvtColor(self._image, cv2.COLOR_RGB2BGR), 0)
        else:
            self._image = cv2.rotate(cv2.cvtColor(self._image, cv2.COLOR_RGB2BGR), cv2.ROTATE_90_CLOCKWISE)

        print(Settings.jpegQuality)
        thread = threading.Thread(target=cv2.imwrite,
                                  args=[os.path.join(self.downloadDir, f'IMG_{self._timeStamp}.jpg'),
                                        self._image,
                                        [int(cv2.IMWRITE_JPEG_QUALITY), Settings.jpegQuality]])
        thread.start()

    def switchLens(self):
        self.imageStreamFromCamera.release()

        self.activeLens = next(self.cyclelens)

        #Reload the Class with the new Camera Lens
        MainPage._switch(self, self.activeLens)


class SettingsPage(Screen, Settings):

    def setSettings(self):
        Settings.jpegQuality = int(self.ids.imageQuality.text) if int(self.ids.imageQuality.text) <= 100 else 100

class WindowManager(ScreenManager):
    pass

class DemoApp(App):
    def build(self):
        kv = Builder.load_file('layout.kv')
        return kv

if __name__ == '__main__':
    DemoApp().run()