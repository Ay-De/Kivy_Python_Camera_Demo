from kivy.utils import platform
from kivy.app import App
from kivy.uix.image import Image
import cv2
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
import time


# Check if platform is android and import permissions for the popup
if (platform == 'android'):
    import permissions

class CamApp(Image):

    #Index of camera to use
    index: int = 0
    #Framerate per seconds at which the images should be drawn again
    fps: int = 30

    previewWidth: int = 960
    previewHeight: int = 1280

    def __init__(self, **kwargs):
        super(CamApp, self).__init__(**kwargs)

        #Connect CV2 to camera
        self.imageStreamFromCamera = cv2.VideoCapture(self.index)

        # create a texture with the same dimensions of the captured image.
        # Will be used to display the image
        self.texture = Texture.create(size=(self.previewWidth, self.previewHeight), colorfmt='bgr')

        #Clock will call a function in a specified interval in seconds
        Clock.schedule_interval(self._drawImage, (1.0/self.fps))


    #Note: dt is not used, but required by kivys Clock.schedule_interval function
    def _drawImage(self, dt):
        #Get image from Camera
        self._retval, self.frame = self.imageStreamFromCamera.read()
        #self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

        self.previewImage = cv2.resize(self.frame,
                                       dsize=(self.previewWidth, self.previewHeight),
                                       interpolation=cv2.INTER_LINEAR)

        #Update the texture to display the actual image
        self.texture.blit_buffer(self.previewImage.tostring(), colorfmt='bgr', bufferfmt='ubyte')

    def captureImage(self):
        image = self.ids['cameraPreview']
        timestr = time.strftime('%Y%m%d_%H%M%S')
        image.export_to_png('IMG_{}.png'.format(timestr))
        #camera.export_to_png('IMG-1.png')
        print('saved')


class DemoApp(App):
    def build(self):
        return CamApp()

if __name__ == '__main__':
    DemoApp().run()