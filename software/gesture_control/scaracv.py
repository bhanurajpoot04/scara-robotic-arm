"""
SCARA Arm - Gesture Control (matches stepper_test_with_gripper.ino exactly)

This version adds DEBUG PRINTING so you can see:
  1. Exactly what string is being sent to Arduino (e.g. "X40\n")
  2. Exactly what Arduino replies back (e.g. "X moving 40 steps... X done. Current position: 40")

This makes it obvious whether the problem is:
  - CV/gesture side (no command ever gets sent -> nothing prints "SENDING:")
  - Serial side (command sent but Arduino never replies -> "SENDING:" prints but no "ARDUINO:")
  - Command format side (Arduino replies "Unknown command" -> command string is malformed)

GESTURES:
  INDEX finger only          -> X axis   (left/right of frame center)
  INDEX + MIDDLE fingers     -> A axis   (left/right of frame center)
  FIST                       -> Gripper OPEN   (sends "G1")
  PALM                       -> Gripper CLOSE  (sends "G0")
  Anything else (e.g. 3+ fingers) -> Z axis  (top/bottom of frame center)

Install: pip install opencv-python mediapipe pyserial
"""

import cv2
import mediapipe as mp
import serial
import time
import math

# =========================== CONFIG - TUNE FOR YOUR SETUP ===========================
SERIAL_PORT = 'COM8'   # run list_ports.py first to confirm this is correct
BAUD = 115200

STEP_BURST = 40         # steps sent per jog command
SEND_INTERVAL = 0.15    # seconds between jog commands
DEAD_ZONE = 0.15        # fraction of frame width/height around center with no motion
# ======================================================================================


def send_command(ser, cmd_str):
    """
    Sends a command EXACTLY the way the .ino expects it and prints:
      - what was sent
      - what Arduino replied (if anything, within a short window)
    cmd_str should be WITHOUT the trailing \\n - this function adds it.
    """
    full = (cmd_str + "\n").encode()
    print(f"SENDING: {cmd_str!r}  (raw bytes: {full!r})")
    ser.write(full)
    ser.flush()

    # give Arduino a moment to process + reply, then read whatever came back
    time.sleep(0.05)
    replied = False
    while ser.in_waiting:
        line = ser.readline().decode(errors='ignore').strip()
        if line:
            print(f"  ARDUINO: {line}")
            replied = True
    if not replied:
        print("  ARDUINO: (no reply received)")


def connect_arduino():
    print(f"Connecting to {SERIAL_PORT} @ {BAUD}...")
    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)
    time.sleep(2)  # wait for Arduino auto-reset on connect

    # drain and print Arduino's boot message ("Stepper test ready." etc.)
    time.sleep(0.3)
    while ser.in_waiting:
        line = ser.readline().decode(errors='ignore').strip()
        if line:
            print(f"  BOOT: {line}")
    print("Connected.\n")
    return ser


def finger_extended(landmarks, tip_id, pip_id):
    return landmarks[tip_id].y < landmarks[pip_id].y


def thumb_extended(landmarks):
    wrist = landmarks[0]
    thumb_tip = landmarks[4]
    thumb_mcp = landmarks[2]
    d_tip = math.hypot(thumb_tip.x - wrist.x, thumb_tip.y - wrist.y)
    d_mcp = math.hypot(thumb_mcp.x - wrist.x, thumb_mcp.y - wrist.y)
    return d_tip > d_mcp * 1.3


def classify_gesture(landmarks):
    index_up = finger_extended(landmarks, 8, 6)
    middle_up = finger_extended(landmarks, 12, 10)
    ring_up = finger_extended(landmarks, 16, 14)
    pinky_up = finger_extended(landmarks, 20, 18)
    thumb_up = thumb_extended(landmarks)

    if not index_up and not middle_up and not ring_up and not pinky_up and not thumb_up:
        return "FIST"
    if index_up and middle_up and ring_up and pinky_up and thumb_up:
        return "PALM"
    if index_up and not middle_up and not ring_up and not pinky_up:
        return "INDEX_ONLY"
    if index_up and middle_up and not ring_up and not pinky_up:
        return "TWO_FINGERS"
    return "OTHER"


def main():
    arduino = connect_arduino()

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.6)

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    last_send = 0.0
    last_gripper_cmd = None
    print("Starting gesture control. Press ESC to quit.\n")

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        status_text = "No hand detected"

        if result.multi_hand_landmarks:
            landmarks = result.multi_hand_landmarks[0].landmark
            mp_draw.draw_landmarks(frame, result.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

            wrist_lm = landmarks[0]
            py_pos = wrist_lm.y * h
            gesture = classify_gesture(landmarks)
            now = time.time()

            if gesture == "FIST":
                status_text = "FIST -> Gripper OPEN (G1)"
                if last_gripper_cmd != "OPEN":
                    send_command(arduino, "G1")
                    last_gripper_cmd = "OPEN"

            elif gesture == "PALM":
                status_text = "PALM -> Gripper CLOSE (G0)"
                if last_gripper_cmd != "CLOSE":
                    send_command(arduino, "G0")
                    last_gripper_cmd = "CLOSE"

            elif gesture == "INDEX_ONLY":
                index_tip = landmarks[8]
                fx = index_tip.x * w
                center_x = w / 2
                dead = DEAD_ZONE * w

                if now - last_send > SEND_INTERVAL:
                    if fx > center_x + dead:
                        send_command(arduino, f"X{STEP_BURST}")
                        status_text = f"INDEX -> X RIGHT (+{STEP_BURST})"
                        last_send = now
                    elif fx < center_x - dead:
                        send_command(arduino, f"X-{STEP_BURST}")
                        status_text = f"INDEX -> X LEFT (-{STEP_BURST})"
                        last_send = now
                    else:
                        status_text = "INDEX -> X (centered, no move)"

            elif gesture == "TWO_FINGERS":
                index_tip = landmarks[8]
                fx = index_tip.x * w
                center_x = w / 2
                dead = DEAD_ZONE * w

                if now - last_send > SEND_INTERVAL:
                    if fx > center_x + dead:
                        send_command(arduino, f"A{STEP_BURST}")
                        status_text = f"TWO_FINGERS -> A RIGHT (+{STEP_BURST})"
                        last_send = now
                    elif fx < center_x - dead:
                        send_command(arduino, f"A-{STEP_BURST}")
                        status_text = f"TWO_FINGERS -> A LEFT (-{STEP_BURST})"
                        last_send = now
                    else:
                        status_text = "TWO_FINGERS -> A (centered, no move)"

            else:  # OTHER -> Z axis mode
                center_y = h / 2
                dead = DEAD_ZONE * h

                if now - last_send > SEND_INTERVAL:
                    if py_pos < center_y - dead:
                        send_command(arduino, f"Z{STEP_BURST}")
                        status_text = f"Z UP (+{STEP_BURST})"
                        last_send = now
                    elif py_pos > center_y + dead:
                        send_command(arduino, f"Z-{STEP_BURST}")
                        status_text = f"Z DOWN (-{STEP_BURST})"
                        last_send = now
                    else:
                        status_text = "Z (centered, no move)"

        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 0), 2)

        cv2.imshow("SCARA Gesture Control (debug)", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    arduino.close()


if __name__ == "__main__":
    main()