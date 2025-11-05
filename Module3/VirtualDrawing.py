# import cv2
# import numpy as np
# import time
# import os
# import HandTrackingModule as htm
#
# # ------------------ Configuration ------------------
# brushThickness = 25
# eraserThickness = 100
# folderPath = "Header"
#
# # ------------------ Load Header Images ------------------
# myList = os.listdir(folderPath)
# print("Header images:", myList)
#
# overlayList = []
# for imPath in myList:
#     image = cv2.imread(f'{folderPath}/{imPath}')
#     overlayList.append(image)
#
# if len(overlayList) == 0:
#     raise ValueError("No header images found in the 'Header' folder!")
#
# print("Loaded Headers:", len(overlayList))
#
# # Resize all header images to the same size (1280x125)
# overlayList = [cv2.resize(img, (1280, 125)) for img in overlayList]
# header = overlayList[0]
# drawColor = (255, 0, 255)
#
# # ------------------ Setup Camera ------------------
# cap = cv2.VideoCapture(1)
# cap.set(3, 1280)  # Width
# cap.set(4, 720)   # Height
#
# detector = htm.handDetector(detectionCon=0.65, maxHands=1)
# xp, yp = 0, 0
# imgCanvas = np.zeros((720, 1280, 3), np.uint8)
#
# # ------------------ Main Loop ------------------
# while True:
#     success, img = cap.read()
#     if not success:
#         print("Failed to capture image from camera.")
#         break
#
#     img = cv2.flip(img, 1)
#
#     # 1. Find Hand Landmarks
#     img = detector.findHands(img)
#     lmList = detector.findPosition(img, draw=False)
#
#     if len(lmList) != 0:
#         # Tip of index and middle fingers
#         x1, y1 = lmList[8][1:]
#         x2, y2 = lmList[12][1:]
#
#         # 2. Check which fingers are up
#         fingers = detector.fingersUp()
#
#         # 3. Selection Mode – Two fingers up
#         if fingers[1] and fingers[2]:
#             xp, yp = 0, 0
#             print("Selection Mode")
#
#             if y1 < 125:
#                 if 250 < x1 < 450:
#                     header = overlayList[0]
#                     drawColor = (255, 0, 255)
#                 elif 550 < x1 < 750:
#                     header = overlayList[1]
#                     drawColor = (255, 0, 0)
#                 elif 800 < x1 < 950:
#                     header = overlayList[2]
#                     drawColor = (0, 255, 0)
#                 elif 1050 < x1 < 1200:
#                     header = overlayList[3]
#                     drawColor = (0, 0, 0)
#
#             cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)
#
#         # 4. Drawing Mode – Index finger up
#         if fingers[1] and not fingers[2]:
#             cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
#             print("Drawing Mode")
#
#             if xp == 0 and yp == 0:
#                 xp, yp = x1, y1
#
#             if drawColor == (0, 0, 0):  # Eraser
#                 cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
#                 cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)
#             else:
#                 cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
#                 cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)
#
#             xp, yp = x1, y1
#
#     # 5. Merge Canvas and Live Image
#     imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
#     _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
#     imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
#     img = cv2.bitwise_and(img, imgInv)
#     img = cv2.bitwise_or(img, imgCanvas)
#
#     # 6. Overlay Header
#     img[0:125, 0:1280] = header
#
#     # 7. Display
#     cv2.imshow("Virtual Drawing", img)
#     cv2.imshow("Canvas", imgCanvas)
#
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()
import cv2
import numpy as np
import time
import os
import HandTrackingModule as htm

#######################
brushThickness = 15
eraserThickness = 50
########################

folderPath = "Header"
myList = os.listdir(folderPath)
print(myList)
overlayList = []
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    if image is not None:
        # Resize all header images to 125x1280
        image = cv2.resize(image, (1280, 125))
        overlayList.append(image)
    else:
        print(f"Failed to load image: {imPath}")
print(len(overlayList))

if overlayList:
    header = overlayList[0]
else:
    # Create a default header if no images loaded
    header = np.zeros((125, 1280, 3), np.uint8)
    cv2.putText(header, "No Header Images Found", (500, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

drawColor = (255, 0, 255)

cap = cv2.VideoCapture(1)
cap.set(3, 1280)
cap.set(4, 720)

# Updated initialization for new MediaPipe version
detector = htm.handDetector(detectionCon=0.7, maxHands=1)
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

while True:
    # 1. Import image
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        break

    img = cv2.flip(img, 1)

    # 2. Find Hand Landmarks
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # tip of index and middle fingers
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # 3. Check which fingers are up
        fingers = detector.fingersUp()

        # 4. If Selection Mode - Two fingers are up
        if fingers[1] and fingers[2]:
            print("Selection Mode")
            # Checking for the click
            if y1 < 125:
                if 250 < x1 < 450:
                    header = overlayList[0] if len(overlayList) > 0 else header
                    drawColor = (255, 0, 255)
                elif 550 < x1 < 750:
                    header = overlayList[1] if len(overlayList) > 1 else header
                    drawColor = (255, 0, 0)
                elif 800 < x1 < 950:
                    header = overlayList[2] if len(overlayList) > 2 else header
                    drawColor = (0, 255, 0)
                elif 1050 < x1 < 1200:
                    header = overlayList[3] if len(overlayList) > 3 else header
                    drawColor = (0, 0, 0)
            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

        # 5. If Drawing Mode - Index finger is up, middle finger down
        if fingers[1] and not fingers[2]:
            cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
            print("Drawing Mode")

            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            # Use eraser for black color, normal brush for others
            if drawColor == (0, 0, 0):
                cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)
            else:
                cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)

            xp, yp = x1, y1
        else:
            # Reset position when not drawing
            xp, yp = 0, 0

    # Convert canvas to grayscale and create inverse mask
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

    # Combine original image with canvas
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    # Setting the header image
    img[0:125, 0:1280] = header

    cv2.imshow("Image", img)
    cv2.imshow("Canvas", imgCanvas)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()