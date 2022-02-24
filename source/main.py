from kivy.utils import platform
from kivy.app import App
from kivy.uix.image import Image
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.screenmanager import Screen, ScreenManager
import threading
import cv2
import time
import os
from pathlib import Path
from itertools import cycle

#Check if platform is android and import permissions for the popup
if (platform == 'android'):
    #Get path to internal Android Storage
    from android.storage import primary_external_storage_path
    import permissions

#This class will contain the user changable settings.
#I.e. JPEG Quality, Saving directory for the images,...
class Settings:

    jpegQuality = 98


#This class is part of the main page, containing the shutterbutton and image preview viewfinder
class MainPage(Image, Screen, Settings):

    def __init__(self, nextLens=0, **kwargs):
        super(MainPage, self).__init__(**kwargs)

        #Framerate per seconds at which the images should be drawn again
        self.fps = 30

        #Setting raw sensor height and width to 10000, to get the highest possible resolution.
        self.rawHeight = 10000
        self.rawWidth = 10000

        #Set storage path for the captured photos according to the used platform
        if (platform == 'android'):
            self.downloadDir = os.path.join(primary_external_storage_path(), 'Download')
        else:
            self.downloadDir = str(Path.home() / 'Downloads')

        #On android, switch width and height, because pictures on phones are usually taken
        #vertically, instead of horizontally like on tablets or laptops
        if platform == 'win':
            self.previewHeight = 940
            self.previewWidth = 1280
        else:
            self.previewHeight = 1280
            self.previewWidth = 940

        self.texture = Texture.create(size=(self.previewWidth, self.previewHeight), colorfmt='rgb')

        #all possible lens id's will be stored here
        self.lenses = []

        #Get id of each usable camera
        for n in range(0, 6):
            self._tempCam = cv2.VideoCapture(n,
                                             cv2.CAP_DSHOW) if (platform == 'win') else cv2.VideoCapture(n,
                                                                                                            cv2.CAP_ANDROID)

            if self._tempCam.isOpened():
                self.lenses.append(n)
                self._tempCam.release()

            else:
                self._tempCam.release()
                break

        #for convenience, make it possible to cycle through the list of lens id's
        self.cyclelens = cycle(self.lenses)

        #call the module to initialize the camera lens
        self._switch(nextLens)

    #Module to connect to the lens. default and starting value is 0
    def _switch(self, nextLens):
        #Index of camera to use
        self.index = nextLens

        #Sync the the next camera lens with the cyclelens output
        ######### NOTE: CHECK IF NECESSARY. SHOULD BE REDUNDANT NOW ##################
        while (nextLens != next(self.cyclelens)):
            next(self.cyclelens)

        #Connect opencv to camera
        if (platform == 'android'):
            self.imageStreamFromCamera = cv2.VideoCapture(self.index, cv2.CAP_ANDROID)
        else:
            self.imageStreamFromCamera = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)

        #Set camera to max resultion if the connection was successful
        if self.imageStreamFromCamera.isOpened():
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FRAME_WIDTH, self.rawWidth)
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.rawHeight)


            self.imageStreamFromCamera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('R','G','B','3'))
            self.imageStreamFromCamera.set(cv2.CAP_PROP_FPS, self.fps)
            self.imageStreamFromCamera.set(cv2.CAP_PROP_BUFFERSIZE, 3)

        #Clock will call a function in a specified interval in seconds
        Clock.schedule_interval(self._drawImage, (1.0 / self.fps))

    #Note: dt is not used, but required by kivys Clock.schedule_interval function
    def _drawImage(self, dt):

        #Get image from Camera
        _retval, self.frame = self.imageStreamFromCamera.read()

        #Check if any frame was returned and if yes, process and display it
        if _retval:

            #Flip and rotate image until the orientation is correct
            ############## NOTE: ADD SETTINGS OPTION TO MANUALLY LET IT BE CORRECTED BY THE USER ##################
            ####### DIFFERENT DEVICES USE DIFFERENT ORIENTATION ###################
            if (platform == 'win'):
                self.frame = cv2.flip(self.frame, 0)
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
            else:
                self.frame = cv2.rotate(self.frame, cv2.ROTATE_90_CLOCKWISE)
                self.frame = cv2.flip(self.frame, 0)

            self.previewImage = cv2.resize(self.frame,
                                        dsize=(self.previewWidth, self.previewHeight),
                                        interpolation=cv2.INTER_NEAREST)

            #Update the texture to display the actual image
            self.texture.blit_buffer(self.previewImage.tostring(), colorfmt='rgb', bufferfmt='ubyte')
            self.canvas.ask_update()

    #This function will save the image if the shutter button has been pressed
    def captureImage(self):

        #Save the image and timestamp in a new variable as a first step. Time critical in image capturing
        self._image = self.frame
        self._timeStamp = time.strftime('%Y%m%d_%H%M%S')

        #Again, correct the image orientation before saving
        if platform == 'win':
            self._image = cv2.flip(cv2.cvtColor(self._image, cv2.COLOR_RGB2BGR), 0)
        else:
            self._image = cv2.flip(cv2.cvtColor(self._image, cv2.COLOR_RGB2BGR), 0)

        #Use a new thread to save the image in the background while displaying the next frames in the viewfinder
        thread = threading.Thread(target=cv2.imwrite,
                                  args=[os.path.join(self.downloadDir, f'IMG_{self._timeStamp}.jpg'),
                                        self._image,
                                        [int(cv2.IMWRITE_JPEG_QUALITY), Settings.jpegQuality]])
        thread.start()

    #This function will switch between the lenses
    def switchLens(self):
        #Stop the opencv connection to the camera
        self.imageStreamFromCamera.release()

        #Get the next lens id which should be activated if the user presses on the button "switch"
        self.activeLens = next(self.cyclelens)

        #Reconnect opencv to the next camera lens
        MainPage._switch(self, self.activeLens)


#This class is part of the second page, the settings page, where the user can make some adjustments.
#All settings will be applied once the user presses on the Settings icon in the upper left corner
#to go back to the viewfinder image.
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