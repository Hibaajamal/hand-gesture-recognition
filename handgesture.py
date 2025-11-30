import cv2
import mediapipe as mp
import keyboard  # pip install keyboard
import time

# Mediapipe hands setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Finger tip landmarks
tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky

# Start webcam
cap = cv2.VideoCapture(0)

# To prevent multiple presses per frame
last_action = None
last_action_time = 0
action_delay = 0.5  # seconds

# Stability variables
prev_fingers = None
stable_count = 0
required_stable = 5

def fingers_up(hand_landmarks):
    fingers = []

    # Thumb
    if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0]-1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for id in range(1, 5):
        if hand_landmarks.landmark[tip_ids[id]].y < hand_landmarks.landmark[tip_ids[id]-2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    action = None
    key = None

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            finger_states = fingers_up(handLms)
            total_fingers = sum(finger_states)  # ✅ define total_fingers here

            # ----- STABILITY CHECK -----
            if total_fingers == prev_fingers:
                stable_count += 1
            else:
                prev_fingers = total_fingers
                stable_count = 1

            if stable_count >= required_stable:
                # Determine action
                if total_fingers == 1:
                    action = "Volume Down"
                    key = "volume down"
                elif total_fingers == 2:
                    action = "Volume Up"
                    key = "volume up"
                elif total_fingers == 3:
                    action = "Next Track"
                    try:
                        keyboard.send("next track")  # Desktop
                        keyboard.send("shift+n")  # YouTube
                    except:
                        pass

                elif total_fingers == 4:
                    action = "previous track"
                    try:
                        keyboard.send("previous track")
                        keyboard.send("shift+p")
                    except:
                        pass
                elif total_fingers == 5:
                    action = "Play/Pause"
                    try:
                        keyboard.send("play/pause media")  # Desktop media players
                        keyboard.send("k")  # YouTube
                    except:
                        pass
                else:
                    action = None
                    key = None

                # Trigger action only if enough time passed
                current_time = time.time()
                if key is not None and (action != last_action or (current_time - last_action_time) > action_delay):
                    try:
                        keyboard.send(key)
                        last_action = action
                        last_action_time = current_time
                    except Exception as e:
                        print(f"Failed to press key {key}: {e}")

            cv2.putText(frame, f'Action: {action}', (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Gesture Media Player", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
