from kivy.utils import platform
from kivy.app import App
from kivy.uix.camera import Camera
import time

# Check if platform is android and import permissions for the popup
if (platform == 'android'):
    import permissions

class CamApp(Camera):
    index = -1
    captureResolution = (1280, 960)

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