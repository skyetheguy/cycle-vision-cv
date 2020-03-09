import jetson.inference
import jetson.utils
import gpio_demo as gpio

net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.25)
camera = jetson.utils.gstCamera(640, 360, "0", "/home/c-vis/cycle-vision-cv/videos/test.yuv")
#camera = jetson.utils.gstCamera(1280, 720)
display = jetson.utils.glDisplay()

gpio.init()
counter = 0
upper = 4
lower = 0 

while display.IsOpen():
    img, width, height = camera.CaptureRGBA()
    detections = net.Detect(img, width, height)
    if len(detections) > 0:
    	counter = counter + 1
    else:
    	counter = counter - 1 
    	if counter < 0:
    		counter = 0
    for detection in detections:#detections in this frame
    	print("Saw an object:    ")
    	print( detection.ClassID, detection.Area, detection.Center )
    	print("\n")
    if counter > upper:
    	gpio.update_blind_spot("right", True)
    else:
    	gpio.update_blind_spot("right", False)
    display.RenderOnce(img, width, height)
    display.SetTitle("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
