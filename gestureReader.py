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

paused = False  # Bool for pausing reading input
request_stop = False  # Bool for when to stop the app
did_read = False  # Controls delays in reading more gestures to prevent repeats
process_delay = 10  # Used to adjust target FPS due to processing delays
one_sec = 1000  # Constant for 1 second
keyboard = Controller()  # Used to control inputs
volume_change = "2"  # Used to control how much volume changes by
def_read_delay = "1"  # Default read delay
def_fps = "30"  # Default target fps
def_volume_up = "Thumbs Up"  # Default volume up gesture
def_volume_down = "Thumbs Down"  # Default volume down gesture
def_play_pause = "Open Palm"  # Default play/pause gesture
def_stop_cam = "Closed Fist"  # Default stop camera gesture
def_pause_cam = "Victory/Peace Sign"  # Default pause reading gesture
gestures_display = ["Thumbs Up", "Thumbs Down", "Open Palm", "Closed Fist", "Victory/Peace Sign"]
gestures_real = ["Thumb_Up", "Thumb_Down", "Open_Palm", "Closed_Fist", "Victory"]


def process_result(result: GestureRecognizerResult, useless1, useless2):
    global did_read
    global request_stop
    global paused
    if not did_read and len(result.gestures) > 0 and result.gestures[0][0].category_name != 'None':
        did_read = True
        gesture = result.gestures[0][0].category_name
        if gesture == "Victory":
            paused = not paused
            print('DEBUG: gesture recognition result: {}'.format(result))
        if not paused:
            print('DEBUG: gesture recognition result: {}'.format(result))
            if gesture == def_volume_up:
                for x in range(int(volume_change)):
                    keyboard.press(Key.media_volume_up)
                    keyboard.release(Key.media_volume_up)
                    time.sleep(0.01)
            elif gesture == def_volume_down:
                for x in range(int(volume_change)):
                    keyboard.press(Key.media_volume_down)
                    keyboard.release(Key.media_volume_down)
                    time.sleep(0.01)
            elif gesture == "Open_Palm":
                keyboard.press(Key.media_play_pause)
                keyboard.release(Key.media_play_pause)
            elif gesture == "Closed_Fist":
                request_stop = True


def return_camera_indexes():
    # checks the first 10 indexes for viable cameras to use
    index = 0
    arr = []
    r = 10
    while r > 0:
        cap = cv.VideoCapture(index)
        if cap.read()[0]:
            arr.append(str(index))
            cap.release()
        index += 1
        r -= 1
    return arr


def run(sel_camera, target_fps, delay_read, volume_change_val, volume_up, volume_down, play_pause,
        stop_cam, pause_cam):
    global def_volume_up, def_volume_down, def_play_pause, def_stop_cam, def_pause_cam
    def_volume_up = volume_up
    def_volume_down = volume_down
    def_play_pause = play_pause
    def_stop_cam = stop_cam
    def_pause_cam = pause_cam
    global volume_change
    volume_change = volume_change_val
    camera = sel_camera.removeprefix("Camera ")
    cam = cv.VideoCapture(int(camera))
    old_time = 0
    timer = 0
    global did_read, request_stop
    with GestureRecognizer.create_from_options(options) as recognizer:
        while not request_stop:
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
            cv.imshow("Debug", img)
            if did_read:
                did_read = False
            else:
                cv.waitKey(round(1000 / target_fps) - process_delay)
    cam.release()
    cv.destroyAllWindows()
    request_stop = False


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

tk.Label(main, text="Gesture Usage:").grid(row=0, column=2)
# Drop downs for changing which gesture does what
tk.Label(main, text="Volume Up:").grid(row=1, column=1)
volume_up_gesture = tk.StringVar(value=def_volume_up)
volume_up_dropdown = ttk.Combobox(main, textvariable=volume_up_gesture,
                                  values=gestures_display)
volume_up_dropdown.grid(row=1, column=3)

tk.Label(main, text="Volume Down:").grid(row=2, column=1)
volume_down_gesture = tk.StringVar(value=def_volume_down)
volume_down_dropdown = ttk.Combobox(main, textvariable=volume_down_gesture,
                                    values=gestures_display)
volume_down_dropdown.grid(row=2, column=3)

tk.Label(main, text="Play/Pause:").grid(row=3, column=1)
play_pause_gesture = tk.StringVar(value=def_play_pause)
play_pause_dropdown = ttk.Combobox(main, textvariable=play_pause_gesture,
                                   values=gestures_display)
play_pause_dropdown.grid(row=3, column=3)

tk.Label(main, text="Close Camera:").grid(row=4, column=1)
stop_cam_gesture = tk.StringVar(value=def_stop_cam)
stop_cam_dropdown = ttk.Combobox(main, textvariable=stop_cam_gesture,
                                 values=gestures_display)
stop_cam_dropdown.grid(row=4, column=3)

tk.Label(main, text="Pause/Unpause Program:").grid(row=5, column=1)
pause_cam_gesture = tk.StringVar(value=def_pause_cam)
pause_cam_dropdown = ttk.Combobox(main, textvariable=pause_cam_gesture,
                                  values=gestures_display)
pause_cam_dropdown.grid(row=5, column=3)

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
tk.Label(main, text="Volume change is a multiple of 2.\nFor example, volume change of 3 means\n"
                    " volume changes by 6 on increase/decrease.").grid(row=10, column=0)
# Volume change field
volume_change_field = tk.Entry(main)
volume_change_field.insert(0, volume_change)
volume_change_field.grid(row=11, column=0)

# Start Button
start_button = tk.Button(main, text="Start", command=lambda: run(camera_sel.get(),
                                                                 int(fps_target.get()),
                                                                 int(read_delay.get()),
                                                                 int(volume_change_field.get()),
                                                                 gestures_real[gestures_display
                                                                 .index(
                                                                     str(volume_up_gesture.get()))],
                                                                 gestures_real[gestures_display
                                                                 .index(
                                                                     str(volume_down_gesture.get()
                                                                         ))],
                                                                 gestures_real[gestures_display
                                                                 .index(
                                                                     str(play_pause_gesture.get()
                                                                         ))],
                                                                 gestures_real[gestures_display
                                                                 .index(
                                                                     str(stop_cam_gesture.get()
                                                                         ))],
                                                                 gestures_real[gestures_display
                                                                 .index(
                                                                     str(pause_cam_gesture.get()
                                                                         ))]
                                                                 ))
start_button.grid(row=12, column=1)

# Run the GUI event loop
main.mainloop()
