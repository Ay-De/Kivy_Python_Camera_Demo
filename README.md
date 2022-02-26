# Kivy_Python_Camera
A simple camera application built to run on Windows or Android. The GUI is created with Kivy, communication with the camera is accomplished with OpenCV and Python.
The Android app is built with buildozer.

This is more of a proof of work concept demo than an actual camera application intended to be used as a daily driver.

## Development Roadmap

| Milestone | Status |
| ------------- | ------------- |
| Create Github repo | ✅|
| Add basic camera feed | ✅|
| Build the app with Buildozer | ✅|
| Create a basic GUI and preview viewfinder | ✅|
| Add a button to switch between camera lenses | ✅|
| Add a settings page with some options like JPEG quality, and so on | ⚠️|
| Try out direct API calls from Python to Android | ❌ |
| Add Github workflow to build new APKs | ✅|
| Add Github workflow to sign build APKs | ❌ |
| Add Github workflow to publish APK to release page | ✅|

Legend:
✅ finished
⚠️ in progress
❌ not started yet

## Known Issues

- Ultrawide camera lenses are producing a black image in the viewfinder and no image is saved if the shutter button is pressed under this scenario.
- After switching between more than two camera lenses, the viewfinder becomes slow

## Used libraries

https://github.com/kivy/kivy

https://github.com/opencv/opencv
