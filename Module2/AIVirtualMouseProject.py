import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import pyautogui

##########################
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7
#########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# Zoom variables
zoom_start_dist = 0
zoom_level = 1
zoom_threshold = 60  # Increased threshold
is_zooming = False
last_zoom_time = 0
zoom_delay = 0.8  # Increased delay

# Scroll variables
scroll_start_y = 0
scroll_threshold = 60  # Increased threshold
is_scrolling = False
scroll_direction = 0
last_scroll_time = 0
scroll_delay = 0.5  # Increased delay

cap = cv2.VideoCapture(1)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()

# Mode indicators
modes = {
    "move": "MOVE MODE",
    "click": "CLICK MODE",
    "scroll": "SCROLL MODE",
    "zoom": "ZOOM MODE"
}
current_mode = "move"


def perform_scroll(direction, amount=120):
    """Perform scrolling with larger amount"""
    try:
        # Method 1: Using pyautogui with larger scroll amount
        scroll_amount = amount if direction > 0 else -amount
        pyautogui.scroll(scroll_amount)
        print(f"Scrolling {'UP' if direction > 0 else 'DOWN'} - Amount: {scroll_amount}")
        return True
    except Exception as e:
        print(f"Scroll error: {e}")
        return False


def perform_zoom(zoom_type):
    """Perform zoom with multiple key presses for stronger effect"""
    try:
        if zoom_type == "in":
            # Multiple zoom in actions
            pyautogui.hotkey('ctrl', '+')  # Zoom in
            pyautogui.hotkey('ctrl', '+')  # Zoom in again for stronger effect
            print("ZOOM IN - Double action")
        else:  # zoom out
            # Multiple zoom out actions
            pyautogui.hotkey('ctrl', '-')  # Zoom out
            pyautogui.hotkey('ctrl', '-')  # Zoom out again for stronger effect
            print("ZOOM OUT - Double action")
        return True
    except Exception as e:
        print(f"Zoom error: {e}")
        return False


def perform_mouse_scroll(direction):
    """Alternative scroll method using mouse wheel"""
    try:
        if direction > 0:
            # Scroll up - multiple clicks
            autopy.mouse.scroll(1)
            autopy.mouse.scroll(1)
            print("Mouse Scroll UP - Double")
        else:
            # Scroll down - multiple clicks
            autopy.mouse.scroll(-1)
            autopy.mouse.scroll(-1)
            print("Mouse Scroll DOWN - Double")
        return True
    except Exception as e:
        print(f"Mouse scroll error: {e}")
        return False


while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    if not success:
        break

    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    # 2. Get the tip of the index and middle fingers
    fingers = []
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        fingers = detector.fingersUp()
    else:
        fingers = [0, 0, 0, 0, 0]

    # 3. Check which fingers are up
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                  (255, 0, 255), 2)

    # Reset mode
    current_mode = "move"

    current_time = time.time()

    # 4. Only Index Finger : Moving Mode
    if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
        current_mode = "move"
        if len(lmList) != 0:
            # Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

    # 5. Both Index and middle fingers are up : Clicking Mode
    elif len(lmList) != 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
        current_mode = "click"
        # Find distance between fingers
        length, img, lineInfo = detector.findDistance(8, 12, img)
        print(f"Click distance: {length}")

        # Click mouse if distance short
        if length < 40:
            cv2.circle(img, (lineInfo[4], lineInfo[5]),
                       15, (0, 255, 0), cv2.FILLED)
            autopy.mouse.click()
            print("Mouse CLICK")

    # 6. Three fingers up (Index, Middle, Ring): Scroll Mode
    elif len(lmList) != 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
        current_mode = "scroll"

        if not is_scrolling:
            scroll_start_y = y1
            is_scrolling = True

        # Calculate scroll distance
        scroll_distance = scroll_start_y - y1

        # Check if enough time has passed since last scroll
        if current_time - last_scroll_time > scroll_delay:
            # Scroll up - moved hand upward
            if scroll_distance > scroll_threshold:
                # Try both methods for better reliability
                perform_scroll(1, 150)  # Large scroll up
                perform_mouse_scroll(1)  # Alternative method
                scroll_direction = 1
                last_scroll_time = current_time
                scroll_start_y = y1  # Reset start position
                cv2.putText(img, "SCROLL UP +++", (50, 150), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            # Scroll down - moved hand downward
            elif scroll_distance < -scroll_threshold:
                # Try both methods for better reliability
                perform_scroll(-1, 150)  # Large scroll down
                perform_mouse_scroll(-1)  # Alternative method
                scroll_direction = -1
                last_scroll_time = current_time
                scroll_start_y = y1  # Reset start position
                cv2.putText(img, "SCROLL DOWN +++", (50, 150), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

        # Visual feedback for scrolling
        cv2.circle(img, (x1, y1), 15, (0, 255, 255), cv2.FILLED)
        cv2.putText(img, f"Scroll: {int(scroll_distance)}", (50, 180), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 2)

    # 7. Four fingers up (Index, Middle, Ring, Pinky): Zoom Mode
    elif len(lmList) != 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
        current_mode = "zoom"

        # Get distance between thumb and index finger for zoom
        zoom_dist, img, zoom_line_info = detector.findDistance(4, 8, img)

        if not is_zooming:
            zoom_start_dist = zoom_dist
            is_zooming = True

        # Calculate zoom change
        zoom_change = zoom_dist - zoom_start_dist

        # Check if enough time has passed since last zoom
        if current_time - last_zoom_time > zoom_delay:
            # Zoom in (fingers spread apart - increased distance)
            if zoom_change > zoom_threshold:
                perform_zoom("in")
                zoom_level += 0.2
                last_zoom_time = current_time
                zoom_start_dist = zoom_dist  # Reset start distance
                cv2.putText(img, "ZOOM IN +++", (50, 200), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)

            # Zoom out (fingers close together - decreased distance)
            elif zoom_change < -zoom_threshold:
                perform_zoom("out")
                zoom_level -= 0.2
                last_zoom_time = current_time
                zoom_start_dist = zoom_dist  # Reset start distance
                cv2.putText(img, "ZOOM OUT +++", (50, 200), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)

        # Visual feedback for zoom
        cv2.circle(img, (zoom_line_info[4], zoom_line_info[5]), 15, (255, 255, 0), cv2.FILLED)
        cv2.putText(img, f"Zoom: {zoom_level:.1f}x", (50, 230), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 2)
        cv2.putText(img, f"Change: {int(zoom_change)}", (50, 250), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 2)

    # Reset states when not in the mode
    if current_mode != "scroll":
        is_scrolling = False
    if current_mode != "zoom":
        is_zooming = False

    # 8. Display instructions
    cv2.putText(img, "1 finger: MOVE", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    cv2.putText(img, "2 fingers: CLICK", (10, 50), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    cv2.putText(img, "3 fingers: SCROLL", (10, 70), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    cv2.putText(img, "4 fingers: ZOOM", (10, 90), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

    # Display current mode with enhanced visuals
    mode_colors = {
        "move": (255, 0, 255),  # Pink
        "click": (0, 255, 0),  # Green
        "scroll": (0, 255, 255),  # Yellow
        "zoom": (255, 255, 0)  # Cyan
    }

    # Mode display with background for better visibility
    cv2.rectangle(img, (5, hCam - 40), (350, hCam - 5), (0, 0, 0), -1)
    cv2.putText(img, f"ACTIVE MODE: {modes[current_mode]}", (10, hCam - 15),
                cv2.FONT_HERSHEY_PLAIN, 1.5, mode_colors[current_mode], 2)

    # Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f"FPS: {int(fps)}", (wCam - 100, 30), cv2.FONT_HERSHEY_PLAIN, 2,
                (255, 0, 0), 2)

    # Display
    cv2.imshow("AI Virtual Mouse - Enhanced Scroll & Zoom", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()