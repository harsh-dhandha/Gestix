import cv2
from pynput.keyboard import Controller, Key
import handtrackingmodule2 as htm
import numpy as np

# Video and hand detection setup
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set the width of the webcam feed
cap.set(4, 480)  # Set the height

detector = htm.handDetector(maxHands=1, detectionCon=0.5, trackCon=0.5)
keyboard = Controller()

# Flags for drawing and pointer mode
drawMode = False  # Are we drawing?
eraseMode = False  # Are we erasing?

# State flags for slide control
previousSlideActive = False  # To prevent repeated slide change to previous
nextSlideActive = False  # To prevent repeated slide change to next

# Create a blank canvas to draw on
canvas = np.zeros((480, 640, 3), dtype=np.uint8)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    
    if len(lmList) != 0:
        fingers = detector.fingersUp()  # Get which fingers are up
        
        # Move to previous slide (left arrow)
        if fingers == [1, 0, 0, 0, 0] and not previousSlideActive:  # Thumb up 👍
            keyboard.press(Key.left)
            keyboard.release(Key.left)
            print("Moving to the previous slide")
            previousSlideActive = True  # Lock this action until gesture is repeated
        
        # Reset previous slide state if gesture is no longer active
        if fingers != [1, 0, 0, 0, 0]:
            previousSlideActive = False
        
        # Move to next slide (right arrow)
        if fingers == [0, 0, 0, 0, 1] and not nextSlideActive:  # Pinkie up 🖖
            keyboard.press(Key.right)
            keyboard.release(Key.right)
            print("Moving to the next slide")
            nextSlideActive = True  # Lock this action until gesture is repeated

        # Reset next slide state if gesture is no longer active
        if fingers != [0, 0, 0, 0, 1]:
            nextSlideActive = False

        # Show pointer (index and middle fingers up)
        if fingers == [0, 1, 1, 0, 0]:  # ✌️ gesture
            print("Showing pointer")
            cv2.circle(img, (lmList[8][1], lmList[8][2]), 12, (0, 255, 0), cv2.FILLED)  # Green pointer
        
        # Draw on the slide (index finger up)
        if fingers == [0, 1, 0, 0, 0]:  # ☝️ gesture
            drawMode = True
            cv2.circle(img, (lmList[8][1], lmList[8][2]), 12, (0, 0, 255), cv2.FILLED)  # Red draw point
            print("Drawing on the slide")
            if drawMode:
                cv2.circle(canvas, (lmList[8][1], lmList[8][2]), 12, (0, 0, 255), cv2.FILLED)  # Draw on the canvas

        # Erase drawings (all fingers up)
        if fingers == [1, 1, 1, 1, 1]:  # 🖐️ gesture
            eraseMode = True
            print("Erasing drawings")
            canvas = np.zeros((480, 640, 3), dtype=np.uint8)  # Clear the canvas
    
    # Overlay the canvas onto the webcam image
    img = cv2.addWeighted(img, 0.5, canvas, 0.5, 0)

    # Show webcam image with drawings
    cv2.imshow("Webcam", img)
    cv2.waitKey(1)
