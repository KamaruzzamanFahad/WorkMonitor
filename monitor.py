import tkinter as tk
import pyautogui
import schedule
import time
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
import os
import threading
from datetime import datetime

# Cloudinary account configuration
cloudinary.config(
    cloud_name="dczzan7us", 
    api_key="788574336458564",
    api_secret="23N6RtNkRYQuthVOTIaJAHCfaOw"
)

# Global variables for time tracking
start_time = None
total_work_time = 0
in_break = False
timer_running = False

def capture_and_upload():
    global start_time, total_work_time, in_break
    if in_break:
        return

    if start_time is None:
        start_time = time.time()

    try:
        screenshot = pyautogui.screenshot()
        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        filename = f"screenshot_User_Fahad_{timestamp}.png"
        screenshot.save(filename)
        response = upload(filename, public_id=filename)
        print(f"Screenshot uploaded to Cloudinary: {filename}")
        os.remove(filename)  # Delete local file after upload
        print(f"Local file deleted: {filename}")

        # Update total work time
        total_work_time = time.time() - start_time
        if not in_break:
            update_total_time_label()

    except Exception as e:
        print(f"Error occurred: {e}")

def take_break():
    global in_break, timer_running
    in_break = True
    timer_running = False
    print("Taking a break...")
    threading.Thread(target=break_timer, daemon=True).start()

def break_timer():
    time.sleep(300)  # Example: 5 minute break
    print("Break over. Resuming work.")
    global in_break
    in_break = False

def restart_task():
    global start_time, total_work_time, in_break, timer_running
    start_time = time.time() - total_work_time
    in_break = False
    timer_running = True
    schedule.clear('upload')  # Clear any scheduled upload tasks
    schedule.every(1).minutes.do(capture_and_upload).tag('upload')
    update_total_time_label()

def start_task():
    global start_time, timer_running
    start_time = time.time()
    timer_running = True
    schedule.every(1).minutes.do(capture_and_upload).tag('upload')
    schedule.every(30).minutes.do(take_break)
    update_total_time_label()
    threading.Thread(target=run_schedule, daemon=True).start()

def update_total_time_label():
    global total_work_time
    if timer_running:
        total_work_time = time.time() - start_time
        hours, rem = divmod(total_work_time, 3600)
        minutes, seconds = divmod(rem, 60)
        if hours > 0:
            total_time_label.config(text=f"Total work time: {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds")
        elif minutes > 0:
            total_time_label.config(text=f"Total work time: {int(minutes)} minutes, {int(seconds)} seconds")
        else:
            total_time_label.config(text=f"Total work time: {int(seconds)} seconds")
    root.after(1000, update_total_time_label)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

def create_gui():
    global total_time_label, root, start_task_button, take_break_button, restart_task_button
    root = tk.Tk()
    root.title("Work Monitor")
    
    # Set initial window size
    root.geometry("400x300")  # Width x Height

    def start_task_wrapper():
        start_task()
        start_task_button.config(state=tk.DISABLED)
        take_break_button.config(state=tk.NORMAL)
        restart_task_button.config(state=tk.DISABLED)

    def take_break_wrapper():
        take_break()
        take_break_button.config(state=tk.DISABLED)
        restart_task_button.config(state=tk.NORMAL)

    def restart_task_wrapper():
        restart_task()
        restart_task_button.config(state=tk.DISABLED)
        take_break_button.config(state=tk.NORMAL)
        start_task_button.config(state=tk.DISABLED)

    start_task_button = tk.Button(root, text="Start Task", command=start_task_wrapper)
    start_task_button.pack()

    take_break_button = tk.Button(root, text="Take Break", command=take_break_wrapper, state=tk.DISABLED)
    take_break_button.pack()

    restart_task_button = tk.Button(root, text="Restart Task", command=restart_task_wrapper, state=tk.DISABLED)
    restart_task_button.pack()

    total_time_label = tk.Label(root, text="Total work time: 0 seconds")
    total_time_label.pack()

    root.mainloop()

if __name__ == "__main__":
    create_gui()
