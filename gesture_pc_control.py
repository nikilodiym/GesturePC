import cv2
import mediapipe as mp
import pyautogui
import subprocess
import webbrowser
import time
import os

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = "hand_landmarker.task"

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=1
)

landmarker = HandLandmarker.create_from_options(options)

pyautogui.PAUSE = 0.1

last_action = ""
last_action_time = 0
cooldown = 3

def distance(a, b):
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5

def detect_gesture(hand):
    wrist = hand[0]

    index_open = distance(hand[8], wrist) > distance(hand[6], wrist)
    middle_open = distance(hand[12], wrist) > distance(hand[10], wrist)
    ring_open = distance(hand[16], wrist) > distance(hand[14], wrist)
    pinky_open = distance(hand[20], wrist) > distance(hand[18], wrist)

    if index_open and middle_open and ring_open and pinky_open:
        return "OPEN_PALM"

    if not index_open and not middle_open and not ring_open and not pinky_open:
        return "FIST"

    if index_open and middle_open and not ring_open and not pinky_open:
        return "VICTORY"

    if index_open and middle_open and ring_open and not pinky_open:
        return "THREE"

    if distance(hand[8], hand[4]) < 0.07 and middle_open and ring_open and pinky_open:
        return "OK"

    return "UNKNOWN"

def open_chrome():
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]

    for path in paths:
        if os.path.exists(path):
            subprocess.Popen([path])
            return

    webbrowser.open("https://www.google.com")

def open_vscode():
    paths = [
        r"C:\Users\Admin\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        r"C:\Program Files\Microsoft VS Code\Code.exe"
    ]

    for path in paths:
        if os.path.exists(path):
            subprocess.Popen([path])
            return

    subprocess.Popen(["cmd", "/c", "start", "code"])

def open_zoom():
    paths = [
        os.path.expandvars(r"%APPDATA%\Zoom\bin\Zoom.exe"),
        os.path.expandvars(r"%APPDATA%\Zoom\bin_00\Zoom.exe"),
        r"C:\Program Files\Zoom\bin\Zoom.exe",
        r"C:\Program Files (x86)\Zoom\bin\Zoom.exe"
    ]

    for path in paths:
        if os.path.exists(path):
            subprocess.Popen([path])
            return

    webbrowser.open("https://zoom.us/join")

def open_telegram():
    paths = [
        os.path.expandvars(r"%APPDATA%\Telegram Desktop\Telegram.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Telegram Desktop\Telegram.exe"),
        r"C:\Program Files\Telegram Desktop\Telegram.exe"
    ]

    for path in paths:
        if os.path.exists(path):
            subprocess.Popen([path])
            return

    webbrowser.open("https://web.telegram.org")

def execute_gesture(gesture):
    global last_action
    global last_action_time

    current_time = time.time()

    if current_time - last_action_time < cooldown:
        return

    if gesture == "OPEN_PALM":
        open_chrome()
        last_action = gesture
        last_action_time = current_time

    elif gesture == "FIST":
        open_vscode()
        last_action = gesture
        last_action_time = current_time

    elif gesture == "VICTORY":
        open_zoom()
        last_action = gesture
        last_action_time = current_time

    elif gesture == "THREE":
        open_telegram()
        last_action = gesture
        last_action_time = current_time

    elif gesture == "OK":
        subprocess.Popen("notepad.exe")
        last_action = gesture
        last_action_time = current_time

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    result = landmarker.detect(mp_image)

    gesture = "UNKNOWN"

    if result.hand_landmarks:
        hand = result.hand_landmarks[0]
        gesture = detect_gesture(hand)

        for landmark in hand:
            x = int(landmark.x * frame.shape[1])
            y = int(landmark.y * frame.shape[0])
            cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

        execute_gesture(gesture)

    cv2.putText(
        frame,
        f"Gesture: {gesture}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        "Q - exit",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.imshow("Gesture PC Control", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
landmarker.close()