import cv2
import mediapipe as mp
import pyautogui
import math
import numpy as np
import time

# Disable FailSafe to prevent crashes at corners
pyautogui.FAILSAFE = False

def main():
    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    mp_draw = mp.solutions.drawing_utils

    # Screen dimensions
    screen_width, screen_height = pyautogui.size()
    
    # Camera setup
    cap = cv2.VideoCapture(0)
    
    # Smoothing variables
    prev_screen_x, prev_screen_y = 0, 0
    curr_screen_x, curr_screen_y = 0, 0
    smoothing = 5
    
    # State variables
    last_click_time = 0
    click_debounce = 0.5 # Seconds between clicks
    
    print("Virtual Mouse Started.")
    print("Gestures:")
    print(" - Index + Middle UP: Move Mouse")
    print(" - Index DOWN (Middle UP): Left Click")
    print(" - Middle DOWN (Index UP): Right Click")
    print(" - All Fingers Closed (Fist): Double Click")
    print(" - Index + Middle + Thumb UP: Scroll")
    print("Press 'Esc' to exit.")

    try:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                continue

            image = cv2.flip(image, 1)
            frame_height, frame_width, _ = image.shape
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_image)
            
            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Get Landmarks
                    lmList = []
                    for id, lm in enumerate(hand_landmarks.landmark):
                        h, w, c = image.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lmList.append([id, cx, cy])
                    
                    if len(lmList) != 0:
                        # Detect Fingers Up/Down
                        fingers = []
                        
                        # Identify Hand (Left or Right)
                        # Note: MediaPipe works on the image it receives. 
                        # Since we flipped the image, a real Right hand looks like a Right hand.
                        # Label is usually correct.
                        label = handedness.classification[0].label
                        
                        # Thumb Logic
                        # For Right Hand: Thumb is on Left. Open if Tip x < IP x.
                        # For Left Hand: Thumb is on Right. Open if Tip x > IP x.
                        if label == "Right":
                            if lmList[4][0] < lmList[3][0]:
                                fingers.append(1)
                            else:
                                fingers.append(0)
                        else: # Left Hand
                            if lmList[4][0] > lmList[3][0]:
                                fingers.append(1)
                            else:
                                fingers.append(0)
                        
                        # 4 Fingers (Index to Pinky) - Check if Tip y < PIP y
                        # This assumes hand is roughly upright.
                        for id in [8, 12, 16, 20]:
                            if lmList[id][2] < lmList[id-2][2]:
                                fingers.append(1)
                            else:
                                fingers.append(0)
                        
                        # Debug: Show Finger States
                        finger_str = str(fingers)
                        cv2.putText(image, f"Fingers: {finger_str}", (10, 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                        cv2.putText(image, f"Hand: {label}", (10, 130), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

                        # --- Gesture Logic ---
                        
                        # 2. Scroll (Index + Middle + Thumb UP)
                        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1:
                            cv2.putText(image, "SCROLL", (50, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
                            y_scroll = lmList[8][2]
                            if y_scroll < frame_height // 3:
                                pyautogui.scroll(20)
                            elif y_scroll > 2 * frame_height // 3:
                                pyautogui.scroll(-20)
                                
                        # 3. Move Mouse (Index + Middle UP)
                        # Relaxed condition: Ignore Thumb if it's not explicitly UP for Scroll?
                        # No, Scroll is 1,1,1. Move is 0,1,1.
                        # If thumb detection is shaky, it might flicker.
                        # Let's strictly enforce Thumb=0 for Move to avoid conflict with Scroll.
                        elif fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0:
                            # Move Mode
                            x1, y1 = lmList[8][1], lmList[8][2]
                            margin = 100
                            x3 = np.interp(x1, (margin, frame_width - margin), (0, screen_width))
                            y3 = np.interp(y1, (margin, frame_height - margin), (0, screen_height))
                            
                            curr_screen_x = prev_screen_x + (x3 - prev_screen_x) / smoothing
                            curr_screen_y = prev_screen_y + (y3 - prev_screen_y) / smoothing
                            
                            pyautogui.moveTo(curr_screen_x, curr_screen_y)
                            prev_screen_x, prev_screen_y = curr_screen_x, curr_screen_y
                            
                            cv2.circle(image, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                            cv2.putText(image, "MOVE", (50, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

                        # 4. Left Click (Index DOWN, Middle UP)
                        elif fingers[1] == 0 and fingers[2] == 1:
                            if time.time() - last_click_time > click_debounce:
                                pyautogui.click()
                                last_click_time = time.time()
                                cv2.putText(image, "LEFT CLICK", (50, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

                        # 5. Right Click (Index UP, Middle DOWN)
                        elif fingers[1] == 1 and fingers[2] == 0:
                             if time.time() - last_click_time > click_debounce:
                                pyautogui.rightClick()
                                last_click_time = time.time()
                                cv2.putText(image, "RIGHT CLICK", (50, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

                        # 6. Double Click (All Fingers Closed / Fist)
                        elif fingers == [0, 0, 0, 0, 0]:
                             if time.time() - last_click_time > click_debounce:
                                pyautogui.doubleClick()
                                last_click_time = time.time()
                                cv2.putText(image, "DOUBLE CLICK", (50, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 0), 3)

            cv2.imshow('Virtual Mouse', image)
            if cv2.waitKey(1) & 0xFF == 27:
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
