import gphoto2cffi as gp
import os


#print(gp.list_cameras())
#cam = gp.Camera()
#img = cam.capture()
os.system("gphoto2 --capture-image")
