"""Quantum Blink webcam companion.

Watches your webcam for blinks and sends them to the Quantum Blink mod
for Outer Wilds.

Normally the mod starts this program for you. You can also run it by hand
to check your camera or tune the sensitivity.

Options:
  --hidden          run without the video window (the mod uses this)
  --parent-pid PID  quit automatically when that program (the game) closes
  --camera N        which webcam to use (0 = default)
  --jump X          blink sensitivity: how far above the resting level counts as a blink

Keys (with the video window selected):
  +  more sensitive (smaller jump needed)
  -  less sensitive (bigger jump needed)
  Q  quit
"""

import argparse
import ctypes
import os
import socket
import sys
import time
from ctypes import wintypes

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision

# Exit codes, so the mod can tell the player what went wrong.
EXIT_OK = 0
EXIT_NO_CAMERA = 2
EXIT_NO_MODEL = 3
EXIT_CAMERA_LOST = 4

GAME_ADDRESS = ("127.0.0.1", 47310)     # this computer, and the port the mod listens on
CONTROL_ADDRESS = ("127.0.0.1", 47311)  # the mod sends settings changes here
SEND_INTERVAL = 0.1                     # also repeat the current state this often (seconds)
BASELINE_SPEED = 0.03                # how quickly the resting level adapts (0 to 1; small = slow)
WINDOW_TITLE = "Quantum Blink companion (press Q to quit)"

# --- Where our files are ---
# Bundled files (the face model) are in sys._MEIPASS when packaged by PyInstaller.
# The log file goes next to the .exe (or the script), where players can find it.
if getattr(sys, "frozen", False):
    BUNDLE_DIR = sys._MEIPASS
    APP_DIR = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = APP_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BUNDLE_DIR, "face_landmarker.task")
LOG_PATH = os.path.join(APP_DIR, "BlinkCompanion.log")

# --- Command-line options ---
parser = argparse.ArgumentParser(description="Quantum Blink webcam companion")
parser.add_argument("--hidden", action="store_true", help="run without the video window")
parser.add_argument("--parent-pid", type=int, help="quit when this process (the game) closes")
parser.add_argument("--camera", type=int, default=0, help="which webcam to use (0 = default)")
parser.add_argument("--jump", type=float, default=0.20, help="blink sensitivity")
args = parser.parse_args()
jump = args.jump

# With no window there's no console to read either, so write messages to a log file instead.
if args.hidden:
    log_file = open(LOG_PATH, "w", encoding="utf-8", buffering=1)  # buffering=1: save each line right away
    sys.stdout = sys.stderr = log_file

# --- Watching the game ---
# Windows lets one program hold a "handle" to another and ask whether it has exited.
SYNCHRONIZE = 0x00100000   # the permission needed to wait on a process
WAIT_TIMEOUT = 0x00000102  # Windows' answer for "still running"

kernel32 = ctypes.WinDLL("kernel32")
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
kernel32.WaitForSingleObject.restype = wintypes.DWORD

parent_handle = None
if args.parent_pid is not None:
    parent_handle = kernel32.OpenProcess(SYNCHRONIZE, False, args.parent_pid)
    if not parent_handle:
        print(f"The game (process {args.parent_pid}) isn't running. Quitting.")
        raise SystemExit(EXIT_OK)


def parent_is_gone():
    # Waiting 0 milliseconds just asks "has it exited yet?" without actually waiting.
    return parent_handle is not None and kernel32.WaitForSingleObject(parent_handle, 0) != WAIT_TIMEOUT


# --- Talking to the game ---
# UDP: a simple one-way message, sent to the game on this same computer.
sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send(message):
    # b"1" = eyes closed, b"0" = eyes open, b"n" = no face found
    try:
        sender.sendto(message, GAME_ADDRESS)
    except OSError:
        pass  # the game isn't listening yet; it will pick up the next message


# The mod can change our settings while we run, so sensitivity changes apply instantly.
# Non-blocking: checking for a message never makes the camera loop wait.
control = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    control.bind(CONTROL_ADDRESS)
    control.setblocking(False)
except OSError:
    print("Can't receive settings changes (is another companion already running?).")
    control = None


def read_control_messages():
    """Applies any settings changes the mod has sent, like b"jump 0.18"."""
    global jump
    while control is not None:
        try:
            data, _ = control.recvfrom(64)
        except OSError:  # includes "nothing waiting right now"
            return
        parts = data.decode("ascii", "ignore").split()
        if len(parts) == 2 and parts[0] == "jump":
            try:
                jump = min(0.90, max(0.02, float(parts[1])))
                print(f"Sensitivity changed: jump {jump:.2f}")
            except ValueError:
                pass


# --- Setup ---
if not os.path.exists(MODEL_PATH):
    print(f"Could not find the face model at {MODEL_PATH}")
    raise SystemExit(EXIT_NO_MODEL)

options = vision.FaceLandmarkerOptions(
    base_options=mp_tasks.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=vision.RunningMode.VIDEO,
    output_face_blendshapes=True,
    num_faces=1,
)

camera = cv2.VideoCapture(args.camera)
if not camera.isOpened():
    print(f"Could not open webcam {args.camera}. Is another program using it?")
    raise SystemExit(EXIT_NO_CAMERA)
camera.set(cv2.CAP_PROP_FPS, 60)

print(f"Quantum Blink companion running (camera {args.camera}, jump {jump:.2f}).")

# --- Main loop ---
with vision.FaceLandmarker.create_from_options(options) as landmarker:
    start = time.monotonic()
    last_timestamp_ms = -1
    baseline = None
    closed = False
    blink_count = 0
    last_message = None
    last_sent = 0.0
    exit_code = EXIT_OK

    while True:
        if parent_is_gone():
            print("The game closed. Quitting.")
            break

        read_control_messages()

        ok, frame = camera.read()
        if not ok:
            print("Lost the webcam feed.")
            exit_code = EXIT_CAMERA_LOST
            break

        now = time.monotonic()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = max(int((now - start) * 1000), last_timestamp_ms + 1)
        last_timestamp_ms = timestamp_ms
        result = landmarker.detect_for_video(image, timestamp_ms)

        if result.face_blendshapes:
            scores = {c.category_name: c.score for c in result.face_blendshapes[0]}
            both = (scores["eyeBlinkLeft"] + scores["eyeBlinkRight"]) / 2

            if baseline is None:
                baseline = both
            rise = both - baseline

            if not closed and rise > jump:
                closed = True
                blink_count += 1
            elif closed and rise < jump / 2:
                closed = False

            if not closed:
                baseline += (both - baseline) * BASELINE_SPEED

            message = b"1" if closed else b"0"
            status = f"rise {rise:+.2f}   jump needed {jump:.2f} (+/-)   blinks {blink_count}"
        else:
            closed = False
            message = b"n"
            status = "No face found"

        # Send right away when the state changes, and repeat it regularly,
        # so the mod knows the companion is still running.
        if message != last_message or now - last_sent >= SEND_INTERVAL:
            send(message)
            last_message = message
            last_sent = now

        if not args.hidden:
            color = (0, 0, 255) if closed else (0, 255, 0)
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.imshow(WINDOW_TITLE, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key in (ord("+"), ord("=")):
                jump = max(0.02, jump - 0.02)
                print(f"Sensitivity: jump {jump:.2f}")
            elif key == ord("-"):
                jump = min(0.90, jump + 0.02)
                print(f"Sensitivity: jump {jump:.2f}")

            # Closing the window with its X button also quits.
            if cv2.getWindowProperty(WINDOW_TITLE, cv2.WND_PROP_VISIBLE) < 1:
                break

send(b"0")  # make sure the game doesn't think the eyes are stuck closed
camera.release()
if not args.hidden:
    cv2.destroyAllWindows()
raise SystemExit(exit_code)
