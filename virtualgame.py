

def virtual():
    import cv2
    from cvzone.HandTrackingModule import HandDetector
    from pynput.keyboard import Key, Controller
    cap = cv2.VideoCapture(0)
    cap.set(3, 320)
    cap.set(4, 210)

    detector = HandDetector(detectionCon=0.7, maxHands=1)
    keyboard = Controller()
    while True:
        _, img = cap.read()
        hands, img = detector.findHands(img)

        if hands:
            finger = detector.fingersUp(hands[0])
            
            if finger == [0, 0, 0, 0, 0]:  # All fingers down
                keyboard.press(Key.left)
                keyboard.release(Key.right)
                keyboard.release(Key.up)
                keyboard.release(Key.down)

            elif finger == [1, 1, 1, 1, 1]:  # All fingers up
                keyboard.press(Key.right)
                keyboard.release(Key.left)
                keyboard.release(Key.up)
                keyboard.release(Key.down)

            elif finger == [0, 1, 0, 0, 0]:  # Only index finger up
                keyboard.press(Key.up)
                keyboard.release(Key.left)
                keyboard.release(Key.right)
                keyboard.release(Key.down)

            elif finger == [0, 1, 1, 0, 0]:  # Index and middle finger up
                keyboard.press(Key.down)
                keyboard.release(Key.left)
                keyboard.release(Key.right)
                keyboard.release(Key.up)

            else:
                # If an unknown finger combo, release all
                keyboard.release(Key.left)
                keyboard.release(Key.right)
                keyboard.release(Key.up)
                keyboard.release(Key.down)

        else:
            # No hand detected — release all keys
            keyboard.release(Key.left)
            keyboard.release(Key.right)
            keyboard.release(Key.up)
            keyboard.release(Key.down)

        cv2.imshow("virtual game controller", img)
        if cv2.waitKey(1) == ord("q"):
            break

if __name__ == "__main__":
    virtual()
