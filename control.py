import cv2
from pynput.keyboard import Controller, Key
from pynput.mouse import Controller as MouseController, Button
import handtrackingmodule2 as htm
import numpy as np
import time

# Video and hand detection setup
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set width
cap.set(4, 480)  # Set height

detector = htm.handDetector(maxHands=1, detectionCon=0.5, trackCon=0.5)
keyboard = Controller()
mouse = MouseController()

# State flags for slide control
previousSlideActive = False
nextSlideActive = False

# Variables for controlling mouse
screenWidth, screenHeight = 1920, 1080  # Set to your screen resolution
smoothening = 7  # Smoothing factor for mouse movement
prevMouseX, prevMouseY = 0, 0
currMouseX, currMouseY = 0, 0

# Variable to store the previous frame width
prevframe = None

# Variables for left-click functionality
clickActive = False  # To ensure single left click
isDragging = False  # To track drag status
pinchStartTime = 0  # To time the pinch gesture for dragging
dragThreshold = 1.0  # Seconds required to enter drag mode
mouseMode = False  # To track if in mouse mode
mouseModeStartTime = 0  # To time when mouse mode starts
mouseModeDelay = 4  # Delay before entering mouse mode

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    if len(lmList) != 0:
        fingers = detector.fingersUp()  # Get which fingers are up

        # Check for entering mouse mode (both thumb and index fingers up)
        if fingers == [1, 1, 0, 0, 0]:  # Thumb and index finger up
            if not mouseMode:  # If not already in mouse mode
                if mouseModeStartTime == 0:  # Start timing when entering the gesture
                    mouseModeStartTime = time.time()  # Start timer for mouse mode delay
                elif time.time() - mouseModeStartTime > mouseModeDelay:  # If delay has passed
                    mouseMode = True  # Enter mouse mode
                    print("Entered Mouse Mode")
            else:
                mouseModeStartTime = 0  # Reset timer if still in mouse mode

        # Mouse control only when in mouse mode
        if mouseMode:
            if fingers == [0, 1, 0, 0, 0]:  
                # Convert hand coordinates to screen coordinates
                x1, y1 = lmList[8][1], lmList[8][2]  # Index finger tip coordinates
                currMouseX = np.interp(x1, (75, 640 - 75), (0, screenWidth)) 
                currMouseY = np.interp(y1, (75, 480 - 75), (0, screenHeight))  

                # Smoothing the movement
                finalMouseX = prevMouseX + (currMouseX - prevMouseX) / smoothening
                finalMouseY = prevMouseY + (currMouseY - prevMouseY) / smoothening

                # Move the mouse
                mouse.position = (screenWidth - finalMouseX, finalMouseY)  # Invert x for natural movement

                prevMouseX, prevMouseY = finalMouseX, finalMouseY  # Update previous positions

        # *** Left Click Gesture***
        if fingers == [1, 1, 0, 0, 0]:  # Thumb and index finger together
            length, _, _ = detector.findDistance(4, 8, img)  # Distance between thumb and index
            if length < 40:  # Pinch gesture detected
                if not clickActive:
                    mouse.click(Button.left, 1)  # Left-click action
                    clickActive = True
                    print("Left Click")
            else:
                clickActive = False  # Reset click for next pinch

        # *** Right Click Gesture***
        if fingers == [1, 1, 1, 0, 0]:

              # Thumb, index, and middle finger pinch
            length1, _, _ = detector.findDistance(4, 8, img)  # Distance between thumb and index
            length2, _, _ = detector.findDistance(4, 12, img) # distance between thumb and middle finger

            if length1 < 40 and length2 < 40:
                if not clickActive :
                    mouse.click(Button.right, 1)  # Right-click action
                    clickActive = True
                    print("Right Click")
                    clickActive = False

        # *** Slide Control ***
        if fingers == [1, 1, 1, 1, 1] and not nextSlideActive:  # Palm gesture for slides
            if prevframe:
                # Slide to next
                if (bbox[2] - prevframe) < -150:
                    keyboard.press(Key.right)
                    keyboard.release(Key.right)
                    print("Moving to the next slide")
                    nextSlideActive = True  # Lock action
                    prevframe = None
                # Slide to previous
                elif (bbox[2] - prevframe) > 150:
                    keyboard.press(Key.left)
                    keyboard.release(Key.left)
                    print("Moving to the previous slide")
                    previousSlideActive = True  # Lock action
                    prevframe = None
            else:
                prevframe = bbox[2]

        # Reset slide control when gesture changes
        if fingers != [1, 1, 1, 1, 1]:
            nextSlideActive = False
            prevframe = None

        # Show pointer (index and middle fingers up)
        if fingers == [0, 1, 1, 0, 0]:  # ✌️ gesture
            print("Showing pointer")
            cv2.circle(img, (lmList[8][1], lmList[8][2]), 12, (0, 255, 0), cv2.FILLED)  # Green pointer

    # Show webcam image
    cv2.imshow("Webcam", img)
    cv2.waitKey(1)



# prevframe = None
# while True:
#     success, img = cap.read()
#     img = detector.findHands(img)
#     lmList, bbox = detector.findPosition(img)
#     if len(lmList) != 0:
#         fingers = detector.fingersUp()  # Get which fingers are up
#         #print(fingers)
#         # Move to previous slide (left arrow)
#         # if fingers == [1, 0, 0, 0, 0] and not previousSlideActive:  # Thumb up 👍
#         #     keyboard.press(Key.left)
#         #     keyboard.release(Key.left)
#         #     print("Moving to the previous slide")
#         #     previousSlideActive = True  # Lock this action until gesture is repeated
        
#         # Reset previous slide state if gesture is no longer active
#         # if fingers != [1, 0, 0, 0, 0]:
#         #     previousSlideActive = False


  # # Draw on the slide (index finger up)
        # if fingers == [0, 1, 0, 0, 0]:  # ☝️ gesture
        #     drawMode = True
        #     cv2.circle(img, (lmList[8][1], lmList[8][2]), 12, (0, 0, 255), cv2.FILLED)  # Red draw point
        #     print("Drawing on the slide")
        #     if drawMode:
        #         cv2.circle(canvas, (lmList[8][1], lmList[8][2]), 12, (0, 0, 255), cv2.FILLED)  # Draw on the canvas

        # # Erase drawings (all fingers up)
        # if fingers == [1, 1, 1, 1, 1]:  # 🖐️ gesture
        #     eraseMode = True
        #     print("Erasing drawings")
        #     canvas = np.zeros((480, 640, 3), dtype=np.uint8)  # Clear the canvas
    
    # # Overlay the canvas onto the webcam image
    # img = cv2.addWeighted(img, 0.5, canvas, 0.5, 0)