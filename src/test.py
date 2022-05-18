#!/usr/bin/env python3
from pickletools import uint8
import cv2
import numpy as np
import json
import rosgraph
import rospy
from ea_ai_msgs.msg import EADetectionsDisplay

detections      = []
numbers         = {}
notification    = ""
warning         = ""
status          = ""
im_w            = 0
im_h            = 0

def detection_cb(data):
    global detections, numbers, im_w, im_h
    detections  = data.boxes
    numbers     = json.loads(data.detection_numbers)
    im_w        = data.image_data.width
    im_h        = data.image_data.height

if __name__ == "__main__":

    rospy.init_node("detection_test", anonymous=False)
    print("Node starting...")

    det_sub = rospy.Subscriber('/detection',EADetectionsDisplay, detection_cb)
    #test_img_orig = cv2.imread("/home/uros/catkin_ws/src/detection_test/src/frame69.png")
    while (im_w == 0 or im_h == 0):
        continue
    test_img_orig = np.ones((im_h,im_w,3), dtype = "uint8")*127
    test_img_orig = cv2.putText(test_img_orig, "Test image",   (int(im_w/2 - im_w/4) ,int(im_h/2)-20),  cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0,0), 3, cv2.LINE_AA)
    while (not rospy.is_shutdown() and rosgraph.is_master_online()):
        try:
            print("Status: ", status)
            test_img = test_img_orig.copy()
            numbers_str = ""
            for att, val in numbers.items():
                numbers_str = numbers_str + str(att) + ":" + str(val) + ","
            numbers_str = numbers_str[:-1]
            test_img = cv2.putText(test_img, numbers_str,   (15,55),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0,255), 2, cv2.LINE_AA)
            test_img = cv2.putText(test_img, notification,  (15,95),  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0,255), 2, cv2.LINE_AA)
            test_img = cv2.putText(test_img, warning,       (15,135), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0,255), 2, cv2.LINE_AA)

            for box in detections:
                tlx = np.clip(int(box.bbox.x_offset-box.bbox.width/2),  0,  im_w)
                tly = np.clip(int(box.bbox.y_offset-box.bbox.height/2), 0,  im_h)
                brx = np.clip(int(box.bbox.x_offset+box.bbox.width/2),  0,  im_w)
                bry = np.clip(int(box.bbox.y_offset+box.bbox.height/2), 0,  im_h)
                
                pt1 = (tlx, tly)
                pt2 = (brx, bry)
                print("pt1", pt1)
                print("pt2", pt2)
                test_img = cv2.rectangle(test_img, pt1,pt2,(box.color.b, box.color.g, box.color.r))
                if (box.text != ""):
                    print ("Using detection text")
                    text_location = (int(box.text_location.x), int(box.text_location.y))
                    if (text_location[0] == 0 and text_location[1] == 0):
                        text_location = (pt1[0], pt1[1]-7)
                    test_img = cv2.putText(test_img, box.text, text_location, cv2.FONT_HERSHEY_SIMPLEX, 1, (box.color.b, box.color.g, box.color.r), 2, cv2.LINE_AA)
               
                elif (box.metadata != ""):
                    print ("Using detection metadata")
                    metadata_str = ""
                    metadata_json = json.loads(box.metadata)
                    for att, val in metadata_json.items():
                        metadata_str = metadata_str + str(att) + ":" + str(val) + ","
                    numbers_str = numbers_str[:-1]

                    text_location = (np.clip(int(box.text_location.x),0,im_w), np.clip(int(box.text_location.y),0,im_h))
                    if (text_location[0] == 0 and text_location[1] == 0):
                        text_location = (pt1[0], pt1[1]-7)
                    test_img = cv2.putText(test_img, metadata_str, text_location, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (box.color.b, box.color.g, box.color.r), 1, cv2.LINE_AA)
            print ("num: ", len(detections))
            cv2.imshow("test", test_img)
            cv2.waitKey(1)
            
        except(KeyboardInterrupt):

            cv2.destroyAllWindows()
            break




cv2.destroyAllWindows()
print("Node exiting...")
