##########################################################################
# This files contains the required android permissions and will
# create a popup asking for them on the first start on Android
#
# See:
# https://developer.android.com/reference/android/Manifest.permission.html
##########################################################################

from android.permissions import request_permissions, Permission

# Specify the required android permissions here.
request_permissions([
    Permission.CAMERA,
    Permission.WRITE_EXTERNAL_STORAGE,
    Permission.READ_EXTERNAL_STORAGE
])