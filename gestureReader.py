import cv2 as cv
import time
import tkinter as tk
from tkinter import ttk
import mediapipe as mp

cam = cv.VideoCapture(0)
oldTime = 0

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode


# Create a gesture recognizer instance with the live stream mode:
def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    print('gesture recognition result: {}'.format(result))


options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='gesture_recognizer.task'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    min_hand_detection_confidence=0.75,
    result_callback=print_result)

main = tk.Tk()
main.title("Gesture Reader Main Menu")

tk.Label(main, text="Camera:").grid(row=0, column=0)
# Camera choice drop down
option_1_var = tk.StringVar(value="Option 1")
dropdown_1 = ttk.Combobox(main, textvariable=option_1_var,
                          values=["Option 1", "Option 2", "Option 3"])
dropdown_1.grid(row=1, column=0)

tk.Label(main, text="Gesture Usage:").grid(row=2, column=0)
# Placeholder for now
option_2_var = tk.StringVar(value="Option A")
dropdown_2 = ttk.Combobox(main, textvariable=option_2_var,
                          values=["Option A", "Option B", "Option C"])
dropdown_2.grid(row=3, column=0)

tk.Label(main, text="Target FPS:").grid(row=4, column=0)
# FPS target field
entry_1 = tk.Entry(main)
entry_1.grid(row=5, column=0)

tk.Label(main, text="Minimum Confidence:").grid(row=6, column=0)
# Minimum confidence field
entry_2 = tk.Entry(main)
entry_2.grid(row=7, column=0)

tk.Label(main, text="Start/Stop On/Off:").grid(row=8, column=0)
# Placeholder for now
checkbox_var = tk.BooleanVar(value=False)
checkbox = tk.Checkbutton(main, text="Check me", variable=checkbox_var)
checkbox.grid(row=9, column=0)

# Start Button
start_button = tk.Button(main, text="Start", command=print("test"))
start_button.grid(row=10, column=0)

# Run the GUI event loop
main.mainloop()

with GestureRecognizer.create_from_options(options) as recognizer:
    timer = 0
    while True:
        timer += 1
        ret, img = cam.read()
        curTime = time.time()
        fps = 1 / (curTime - oldTime)
        oldTime = curTime
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
        recognizer.recognize_async(mp_image, timer)
        cv.putText(img, f"FPS: {int(fps)}", (0, 70), cv.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 2)
        cv.imshow("Output", img)
        cv.waitKey(200)
