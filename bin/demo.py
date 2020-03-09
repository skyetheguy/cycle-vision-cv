import jetson.inference
import jetson.utils
#import gpio_demo as gpio

net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.25)
camera = jetson.utils.gstCamera(640, 360, "0", "/home/c-vis/cycle-vision-cv/videos/test.yuv")
#camera = jetson.utils.gstCamera(1280, 720)
display = jetson.utils.glDisplay()

#gpio.init()
counter = 0
upper_thresh = 2
lower_thresh = 0
upper_ceil = 10
lower_ceil = 0 

while display.IsOpen():
    img, width, height = camera.CaptureRGBA()
    detections = net.Detect(img, width, height)
    
    if len(detections) == 0:
        counter = counter - 1 if counter > lower_ceil else lower_ceil

    for detection in detections:#detections in this frame
        if detection.Confidence > 0.25 and detection.Area > 2000:
            counter = counter + 1 if counter < upper_ceil else upper_ceil
        # else:
            # counter = counter - 1 if counter > lower_ceil else lower_ceil
    	# print("Saw an object:    ")
    	# print( detection.ClassID, detection.Area, detection.Center )
    	# print("\n")
    if counter > upper_thresh:
    	# gpio.update_blind_spot("right", True)
        print("---------------  LIGHT ON  ----------------")
        print(counter)
    else:
    	# gpio.update_blind_spot("right", False)
        print("---------------  LIGHT OFF  ----------------")
        print(counter)
    display.RenderOnce(img, width, height)
    display.SetTitle("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
