import jetson.inference
import jetson.utils
import gpio_demo as gpio

net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.25)
camera = jetson.utils.gstCamera(640, 360, "0", "/home/c-vis/cycle-vision-cv/videos/test.yuv")
#camera = jetson.utils.gstCamera(1280, 720)
display = jetson.utils.glDisplay()

gpio.init()
gpio.update_blind_spot("left", True)

while display.IsOpen():
    img, width, height = camera.CaptureRGBA()
    detections = net.Detect(img, width, height)
    for detection in detections:
    	print("Saw an object:    ")
    	print( detection.ClassID, detection.Area, detection.Center )
    	print("\n")

    display.RenderOnce(img, width, height)
    display.SetTitle("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
