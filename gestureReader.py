import cv2 as cv
import time
import tkinter as tk
from tkinter import ttk
import mediapipe as mp
from pynput.keyboard import Key, Controller

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

did_read = False  # Controls delays in reading more gestures to prevent repeats
process_delay = 10  # Used to adjust target FPS due to processing delays
one_sec = 1000  # Constant for 1 second
keyboard = Controller()  # Used to control inputs
volume_change = 2  # Used to control how much volume changes by
def_read_delay = 2  # Default read delay
def_fps = 30    # Default target fps


def process_result(result: GestureRecognizerResult, useless1, useless2):
    global did_read
    if not did_read and len(result.gestures) > 0 and result.gestures[0][0].category_name != 'None':
        did_read = True
        gesture = result.gestures[0][0].category_name
        print('DEBUG: gesture recognition result: {}'.format(result))
        if gesture == "Thumb_Up":
            for x in range(volume_change):
                keyboard.press(Key.media_volume_up)
                keyboard.release(Key.media_volume_up)
                time.sleep(0.01)
        elif gesture == "Thumb_Down":
            for x in range(volume_change):
                keyboard.press(Key.media_volume_down)
                keyboard.release(Key.media_volume_down)
                time.sleep(0.01)
        elif gesture == "Open_Palm":
            keyboard.press(Key.media_play_pause)
            keyboard.release(Key.media_play_pause)


def return_camera_indexes():
    # checks the first 10 indexes for viable cameras to use
    index = 0
    arr = []
    i = 10
    while i > 0:
        cap = cv.VideoCapture(index)
        if cap.read()[0]:
            arr.append(str(index))
            cap.release()
        index += 1
        i -= 1
    return arr


def run(sel_camera, target_fps, delay_read, volume_change_val):
    global volume_change
    volume_change = volume_change_val
    camera = sel_camera.removeprefix("Camera ")
    cam = cv.VideoCapture(int(camera))
    old_time = 0
    timer = 0
    global did_read
    with GestureRecognizer.create_from_options(options) as recognizer:
        while True:
            timer += 1
            ret, img = cam.read()
            cur_time = time.time()
            fps = 1 / (cur_time - old_time)
            old_time = cur_time
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
            recognizer.recognize_async(mp_image, timer)
            if did_read:
                print("DEBUG: Read valid input, delaying next read...")
                cv.waitKey(delay_read * one_sec)
            cv.putText(img, f"FPS: {int(fps)}", (0, 70), cv.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 2)
            cv.imshow("Output", img)
            if did_read:
                did_read = False
            else:
                cv.waitKey(round(1000 / target_fps) - process_delay)


options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='gesture_recognizer.task'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    min_hand_detection_confidence=0.50,
    result_callback=process_result)

main = tk.Tk()
main.title("Gesture Reader Main Menu")

tk.Label(main, text="Camera:").grid(row=0, column=0)
# Camera choice drop down
cameras = return_camera_indexes()
for i in range(0, len(cameras)):
    cameras[i] = f'Camera {cameras[i]}'
camera_sel = tk.StringVar(value=str(cameras[0]))
camera_sel_dropdown = ttk.Combobox(main, textvariable=camera_sel,
                                   values=cameras)
camera_sel_dropdown.grid(row=1, column=0)

tk.Label(main, text="Gesture Usage:").grid(row=2, column=0)
# Placeholder for now
option_2_var = tk.StringVar(value="Option A")
dropdown_2 = ttk.Combobox(main, textvariable=option_2_var,
                          values=["Option A", "Option B", "Option C"])
dropdown_2.grid(row=3, column=0)

tk.Label(main, text="Target FPS:").grid(row=4, column=0)
# FPS target field
fps_target = tk.Entry(main)
fps_target.insert(0, def_fps)
fps_target.grid(row=5, column=0)

tk.Label(main, text="Read Delay (sec):").grid(row=7, column=0)
# Read delay field
read_delay = tk.Entry(main)
read_delay.insert(0, def_read_delay)
read_delay.grid(row=8, column=0)

tk.Label(main, text="Volume Change:").grid(row=9, column=0)
tk.Label(main, text="Volume change is a multiple of 2. For example, volume change of 3 means"
                    " volume changes by 6 on increase/decrease.").grid(row=10, column=0)
# Volume change field
volume_change_field = tk.Entry(main)
volume_change_field.insert(0, volume_change)
volume_change_field.grid(row=11, column=0)

tk.Label(main, text="Start/Stop On/Off:").grid(row=12, column=0)
# Placeholder for now
checkbox_var = tk.BooleanVar(value=False)
checkbox = tk.Checkbutton(main, text="True/False", variable=checkbox_var)
checkbox.grid(row=13, column=0)

# Start Button
start_button = tk.Button(main, text="Start", command=lambda: run(camera_sel.get(),
                                                                 int(fps_target.get()),
                                                                 int(read_delay.get()),
                                                                 int(volume_change_field.get())
                                                                 ))
start_button.grid(row=14, column=0)

# Run the GUI event loop
main.mainloop()
