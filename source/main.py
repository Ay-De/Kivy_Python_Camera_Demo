from kivy.utils import platform
from kivy.app import App
from kivy.uix.image import Image
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
import cv2
import time

# Check if platform is android and import permissions for the popup
if (platform == 'android'):
    import permissions

class MainPage(Screen):
    pass

class SettingsPage(Screen):
    pass

class WindowManager(ScreenManager):
    pass

class CamApp(Image):

    #Index of camera to use
    index: int = 0
    #Framerate per seconds at which the images should be drawn again
    fps: int = 30

    previewWidth: int = 1280
    previewHeight: int = 960

    def __init__(self, **kwargs):
        super(CamApp, self).__init__(**kwargs)

        #Connect CV2 to camera
        if (platform == 'android'):
            self.imageStreamFromCamera = cv2.VideoCapture(self.index)
        else:
            self.imageStreamFromCamera = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)

        #Clock will call a function in a specified interval in seconds
        Clock.schedule_interval(self._drawImage, (1.0/self.fps))

        #self.btn = self.ids.main.ids.cameraPreview.ids.saveImgBtn
        #btn.bind(on_press=self.captureImage())

    #Note: dt is not used, but required by kivys Clock.schedule_interval function
    def _drawImage(self, dt):
        #Get image from Camera
        self._retval, self.frame = self.imageStreamFromCamera.read()
        #self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

        #Check if any frame was returned and if yes, process and display it
        if self._retval:
            self.frame = cv2.flip(self.frame, 0)

            # create a texture with the same dimensions of the captured image.
            # Will be used to display the image
            self.texture = Texture.create(size=(self.previewWidth, self.previewHeight), colorfmt='bgr')

            self.previewImage = cv2.resize(self.frame,
                                           dsize=(self.previewWidth, self.previewHeight),
                                           interpolation=cv2.INTER_AREA)

            #Update the texture to display the actual image
            self.texture.blit_buffer(self.previewImage.tostring(), colorfmt='bgr', bufferfmt='ubyte')
            #self.ids.cameraPreview = self.texture

    def captureImage(self):
        self.image = cv2.flip(self.frame, 0)
        self.timeStamp = time.strftime('%Y%m%d_%H%M%S')
        cv2.imwrite('IMG_{}.jpg'.format(self.timeStamp), self.image)
        print('image saved')


kv = Builder.load_file('layout.kv')

class DemoApp(App):
    def build(self):
        return kv

if __name__ == '__main__':
    DemoApp().run()