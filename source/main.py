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

from jnius import autoclass

# Check if platform is android and import permissions for the popup
if (platform == 'android'):
    import permissions

class MainPage(Image, Screen):

    #Index of camera to use
    index: int = 0
    #Framerate per seconds at which the images should be drawn again
    fps: int = 30

    rawHeight = 1280
    rawWidth = 960
    jpegQuality = 100 #in %
    previewHeight: int = 1280
    previewWidth: int = 960

    def __init__(self, **kwargs):
        super(MainPage, self).__init__(**kwargs)

        self.texture = Texture.create(size=(self.previewWidth, self.previewHeight), colorfmt='bgr')

        #Connect CV2 to camera
        if (platform == 'android'):
            self.imageStreamFromCamera = cv2.VideoCapture(self.index)
        else:
            self.imageStreamFromCamera = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
            #self.imageStreamFromCamera.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        if self.imageStreamFromCamera.isOpened():
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.rawHeight)
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FRAME_WIDTH, self.rawWidth)
        #Clock will call a function in a specified interval in seconds
        Clock.schedule_interval(self._drawImage, (1.0/self.fps))

    #Note: dt is not used, but required by kivys Clock.schedule_interval function
    def _drawImage(self, dt):
        #Get image from Camera
        _retval, self.frame = self.imageStreamFromCamera.read()

        #self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

        #Check if any frame was returned and if yes, process and display it
        #if _retval:
        if (platform == 'android'):
            self.frame = cv2.flip(self.frame, 1)
        else:
            self.frame = cv2.flip(self.frame, 0)

        self.previewImage = cv2.resize(self.frame,
                                       dsize=(self.previewWidth, self.previewHeight),
                                       interpolation=cv2.INTER_AREA)


        #Update the texture to display the actual image
        self.texture.blit_buffer(self.previewImage.tostring(), colorfmt='bgr', bufferfmt='ubyte')
        self.canvas.ask_update()
        #self.disp = self.ids.cameraPreview.canvas.get_group('display')[0]
        #self.ids.saveImgBtn.canvas.ask_update()
        #self.disp.texture = self.texture
        #self.disp = self.ids.cameraPreview.canvas.clear()
        #self.disp.size = (self.previewWidth, self.previewHeight)
       # self.disp.texture = self.texture
        #self.ids.cameraPreview.canvas.ask_update()
        #self.ids.cameraPreview.texture = self.texture

    def captureImage(self):

        self.timeStamp = time.strftime('%Y%m%d_%H%M%S')
      #  thread = threading.Thread(target=cv2.imwrite,
      #                            args=[f'IMG_{self.timeStamp}.jpg',
      #                                  self.frame,
      #                                  [int(cv2.IMWRITE_JPEG_QUALITY), self.jpegQuality]])
      #  thread.start()

        cv2.imwrite(f'IMG_{self.timeStamp}.jpg', self.frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpegQuality])


class SettingsPage(Screen):
    pass

class WindowManager(ScreenManager):

    Camera = autoclass('android.hardware.Camera')
    print(list(Camera.open(0).getParameters().getSupportedPictureSizes()))
    pass


class DemoApp(App):
    def build(self):
        kv = Builder.load_file('layout.kv')
        return kv

if __name__ == '__main__':
    DemoApp().run()
