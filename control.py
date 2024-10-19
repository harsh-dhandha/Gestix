import cv2
from pynput.keyboard import Controller, Key
from pynput.mouse import Controller as MouseController, Button
import handtrackingmodule2 as htm
import numpy as np
import time
import pyautogui

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640) 
cap.set(4, 480)

detector = htm.handDetector(maxHands=1, detectionCon=0.5, trackCon=0.5)
keyboard = Controller()
mouse = MouseController()

# State flags for slide control
previousSlideActive = False
nextSlideActive = False

#controlling mouse
screenWidth, screenHeight = 1920, 1080  
smoothening = 5  # Smoothing factor for mouse movement
prevMouseX, prevMouseY = 0, 0
currMouseX, currMouseY = 0, 0

# previous frame
prevframe = None

# Variables for dragging functionality
dragMode = False
pinchStartTime = 0
dragThreshold = 3.0  


# Variables for scrolling feature
scrollActive = False  # To track if scrolling is active
prevScrollY = None  # Previous Y-coordinate to compare for scrolling

clickActive = False  # To ensure single left click
mouseMode = False  # To track if in mouse mode
mouseModeStartTime = 0  # To time when mouse mode starts
mouseModeDelay = 5  # Delay before entering mouse mode

# Hyper-click control (to avoid too fast clicks)
clickCooldown = 0.5  # Delay between double-clicks
lastClickTime = 0

# # Variables for zoom mode
# zoomMode = False  # To track zoom mode state
# zoomModeActive = False  # To ensure one-time zoom action
# zoomModeStartTime = 0  # Start time for entering zoom mode
# zoomModeDelay = 5  # Delay before entering zoom mode
# zoomInActive = False
# zoomOutActive = False

while True:
    success, img = cap.read()
    
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    if len(lmList) != 0:
        fingers = detector.fingersUp()
        currentTime = time.time()  
        cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20), 
                      (bbox[2] + 20, bbox[3] + 20), 
                      (0, 255, 0), 2)
        
        # Identifying the hand (left or right) based on thumb position
        if lmList[4][1] < lmList[17][1]:  
            handType = "Left"
        else:  
            handType = "Right"
        
        cv2.putText(img, handType, (bbox[0] - 30, bbox[1] - 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Check for entering mouse mode (both thumb and index fingers up)
        if fingers == [1, 1, 0, 0, 0]:  
            if not mouseMode:  # If not already in mouse mode
                if mouseModeStartTime == 0:  
                    mouseModeStartTime = time.time()  # Start timer for mouse mode delay
                elif time.time() - mouseModeStartTime > mouseModeDelay: 
                    mouseMode = True  # Enter mouse mode
                    print("Entered Mouse Mode")
            else:
                mouseModeStartTime = 0  # Reset timer if still in mouse mode
        # Mouse control only when in mouse mode
        if not dragMode:
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
                    
        #Drag mode
        if detector.findFullPinch(img):  # Full pinch detected
            if not dragMode:
                # Start drag mode
                pyautogui.mouseDown()  # Hold the mouse down (start dragging)
                pinchStartTime = time.time()  # Start timing for drag mode
                dragMode = True
                print("Started dragging")

            # Move the mouse during drag mode
            x1, y1 = lmList[8][1], lmList[8][2]  # Index finger tip coordinates
            currMouseX = np.interp(x1, (75, 640 - 75), (0, screenWidth))
            currMouseY = np.interp(y1, (75, 480 - 75), (0, screenHeight))

            # Smoothing the movement
            finalMouseX = prevMouseX + (currMouseX - prevMouseX) / smoothening
            finalMouseY = prevMouseY + (currMouseY - prevMouseY) / smoothening

            # Move the mouse
            pyautogui.moveTo(screenWidth - finalMouseX, finalMouseY)

            prevMouseX, prevMouseY = finalMouseX, finalMouseY  # Update previous positions

        else:
            # Release drag mode when pinch is released
            if dragMode:
                pyautogui.mouseUp()  # Release the mouse (drop item)
                dragMode = False
                print("Stopped dragging")

        

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
            else:
                clickActive = False

        # if fingers == [1, 1, 0, 0, 0]:  # Thumb and index finger together
        #         if not isDragging:
        #             # Start drag if the pinch gesture is held for long enough
        #             if pinchStartTime == 0:
        #                 pinchStartTime = time.time()
        #             elif time.time() - pinchStartTime > dragThreshold:  # Check if held long enough
        #                 isDragging = True
        #                 mouse.click(Button.left)  # Start dragging
        #                 print("Started dragging")
        #         else:
        #             # While dragging, keep moving the mouse
        #             mouse.position = (screenWidth - finalMouseX, finalMouseY)  # Update mouse position while dragging

        # else:
        #         if isDragging:  # If we are not in a pinch gesture anymore
        #             mouse.release(Button.left)  # Release mouse button
        #             isDragging = False
        #             pinchStartTime = 0  # Reset pinch timing
        #             print("Stopped dragging")
            
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
        
        # *** Scroll Control ***
        if fingers == [1, 1, 1, 1, 1]:  
                if prevScrollY is None:  # Set initial scroll reference point
                    prevScrollY = bbox[1]  #use y coordinate

                # Calculate vertical movement distance
                distanceY = bbox[1] - prevScrollY  

                if abs(distanceY) > 20:  # Only scroll if the movement is significant enough
                    if distanceY < 0:  # Hand moved up, scroll up
                        pyautogui.scroll(150)  
                        print("Scrolling Up")
                    else:  # Hand moved down, scroll down
                        pyautogui.scroll(-150)  
                        print("Scrolling Down")
                
                prevScrollY = bbox[1]  # Update for the next frame

        else:
                prevScrollY = None  # Reset scroll tracking if not in scroll gesture

        # Reset slide control when gesture changes
        if fingers != [1, 1, 1, 1, 1]:
            nextSlideActive = False
            prevframe = None

        # Show pointer (index and middle fingers up)
        if fingers == [0, 1, 1, 0, 0]:  # ✌️ gesture
            print("Showing pointer")
            cv2.circle(img, (lmList[8][1], lmList[8][2]), 12, (0, 255, 0), cv2.FILLED)  # Green pointer
        
        # # Zoom In/Out mode control (Index and Middle finger gesture)
        # if fingers == [0, 1, 1, 0, 0]:  # Gesture for zoom in/out
        #     if not zoomMode:  # Check if not already in zoom mode
        #         if zoomModeStartTime == 0:
        #             zoomModeStartTime = time.time()  # Start the timer
        #         elif time.time() - zoomModeStartTime > zoomModeDelay: 
        #             zoomMode = True  # Enter zoom mode after delay
        #             print("Entered Zoom Mode")
        #     else:
        #         zoomModeStartTime = 0  # Reset the timer if gesture is still showing
        
        # # Exit zoom mode when the same gesture is shown again
        # elif zoomMode and fingers == [0, 1, 1, 0, 0]:
        #     zoomMode = False
        #     zoomModeActive = False  # Reset zoom activity
        #     print("Exited Zoom Mode")

        # # Reset zoomModeStartTime if gesture changes before delay
        # if fingers != [0, 1, 1, 0, 0]:
        #     zoomModeStartTime = 0

        # # Handle zoom in/out based on the zoom mode being active
        # if zoomMode and not zoomModeActive:
        #     if fingers == [0, 1, 1, 1, 1] and not zoomInActive:  # Gesture for zoom in
        #         keyboard.press(Key.ctrl_l)
        #         keyboard.press('+')
        #         keyboard.release('+')
        #         keyboard.release(Key.ctrl_l)
        #         zoomInActive = True
        #         zoomOutActive = False
        #         zoomModeActive = True  # Zoom in executed once
        #         print("Zooming In")

        #     elif fingers == [0, 1, 1, 1, 0] and not zoomOutActive:  # Gesture for zoom out
        #         keyboard.press(Key.ctrl_l)
        #         keyboard.press('-')
        #         keyboard.release('-')
        #         keyboard.release(Key.ctrl_l)
        #         zoomOutActive = True
        #         zoomInActive = False
        #         zoomModeActive = True  # Zoom out executed once
        #         print("Zooming Out")

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