'''
Timetracker to track workinghours
requires module PIL ( pip install Pillow)
'''
import datetime
import os
import sys
from pathlib import Path
import tkinter as tk
import tkinter.messagebox

from PIL import ImageTk, Image

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = Path(__file__).parent.absolute()

    return os.path.join(base_path, relative_path)

class WorkingHoursTracker:
    def __init__(self, master):
        self.master = master
        master.title("Working Hours Tracker")

        self.timers = []
        self.timer_frames = []
        self.timer_labels = []
        self.action_buttons = []
        self.total_labels = []
        self.reset_buttons = []
        self.remove_buttons = []

        self.start_icon = self.resize_icon(resource_path("images/start_icon.png"), 0.25)
        self.stop_icon = self.resize_icon(resource_path("images/stop_icon.png"), 0.25)

        # button to add another time-tracker
        self.add_timer_button = tk.Button(master, text="Add Tracker", command=self.add_timer)
        self.add_timer_button.pack()
        # button to save the current confugration
        self.save_button = tk.Button(master, text="Save Configuration", command=self.save_configuration)
        self.save_button.pack()
        # button to reset all timers
        self.reset_all_button = tk.Button(master, text="Reset All Trackers", command=self.reset_all_timers)
        self.reset_all_button.pack()

        # Load configuration from file
        self.load_configuration()
        
    
    # method to resize icons
    def resize_icon(self, filename, scale):
        image = Image.open(filename)
        width = int(image.width * scale)
        height = int(image.height * scale)
        resized_image = image.resize((width, height))
        return ImageTk.PhotoImage(resized_image)

    def load_configuration(self):
        if not os.path.exists("config.txt"):
            self.show_message("Config file not found. Starting with default configuration.")
            return

        try:
            with open("config.txt", "r") as file:
                lines = file.readlines()
                for line in lines:
                    if  line.strip() != "":
                        timer_info = line.strip().split(",")
                        if len(timer_info) >= 4:
                            timer_label = timer_info[0]
                            total_hours = int(timer_info[1])
                            total_minutes = int(timer_info[2])
                            total_seconds = int(timer_info[3])
                            self.add_timer(timer_label, total_hours, total_minutes, total_seconds)
                        else:
                            self.add_timer(timer_info[0])
        except FileNotFoundError:
            self.show_message("Config file not found. Starting with default configuration.")


    def save_configuration(self):
        print("Saving configuration")
        try:
            if not os.path.exists("config.txt"):
                open("config.txt", "w").close()

            with open("config.txt", "w") as f:
                for i, timer_label in enumerate(self.timer_labels):
                    label_text = timer_label.get()
                    total_hours = self.timers[i]["total_hours"]
                    total_minutes = self.timers[i]["total_minutes"]
                    total_seconds = self.timers[i]["total_seconds"]
                    f.write(f"{label_text},{total_hours},{total_minutes},{total_seconds}\n")

            self.show_message("Configuration saved successfully!")
        except Exception as e:
            error_message = "An error occurred while saving the configuration:\n{}".format(str(e))
            self.show_message(error_message)
            
            
    def save_configuration_and_quit(self):
        self.save_configuration()
        root.after(2000, root.destroy)
         

    def show_message(self, message):
       tkinter.messagebox.showinfo("Message", message,)

    def add_timer(self, timer_label=None, total_hours=0, total_minutes=0, total_seconds=0):
        timer_frame = tk.Frame(self.master)
        timer_frame.pack()

        action_button = tk.Button(timer_frame, image=self.start_icon, command=lambda index=len(self.timers): self.start_stop_timer(index))
        action_button.pack(side=tk.LEFT)
        self.action_buttons.append(action_button)

        if timer_label:
            entry_text = tk.StringVar(value=timer_label)
        else:
            entry_text = tk.StringVar()

        timer_entry = tk.Entry(timer_frame, textvariable=entry_text)
        timer_entry.pack(side=tk.LEFT)
        self.timer_labels.append(timer_entry)

        total_label = tk.Label(timer_frame, text=" {} hours {} minutes {} seconds".format(total_hours, total_minutes, total_seconds))
        total_label.pack(side=tk.LEFT)
        self.total_labels.append(total_label)

        reset_button = tk.Button(timer_frame, text="Reset Tracker", command=lambda index=len(self.timers): self.reset_timer(index))
        reset_button.pack(side=tk.LEFT)
        self.reset_buttons.append(reset_button)
        
        remove_button = tk.Button(timer_frame, text="Remove Tracker", command=lambda index=len(self.timers): self.remove_timer(timer_frame))
        remove_button.pack(side=tk.LEFT)
        self.remove_buttons.append(remove_button)
        

        self.timers.append({
            "tracking": False,
            "start_time": None,
            "total_hours": total_hours,
            "total_minutes": total_minutes,
            "total_seconds": total_seconds,
            "frame": timer_frame,          
        })

    def start_stop_timer(self, timer_index):
        print("Startstopping timer")
        for i, timer in enumerate(self.timers):
            if i == timer_index:
                if not timer["tracking"]:
                    timer["tracking"] = True
                    timer["start_time"] = datetime.datetime.now()
                    self.action_buttons[timer_index].config(image=self.stop_icon)
                else:
                    timer["tracking"] = False
                    elapsed_time = datetime.datetime.now() - timer["start_time"]
                    hours, remainder = divmod(elapsed_time.total_seconds(), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    self.action_buttons[timer_index].config(image=self.start_icon)
                    self.total_labels[timer_index].config(text="Total working time: {} hours {} minutes {} seconds".format(timer["total_hours"], timer["total_minutes"], timer["total_seconds"]))
            else:
                if timer["tracking"]:
                    timer["tracking"] = False
                    elapsed_time = datetime.datetime.now() - timer["start_time"]
                    hours, remainder = divmod(elapsed_time.total_seconds(), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    self.action_buttons[i].config(image=self.start_icon)
                    self.total_labels[i].config(text="Total working time: {} hours {} minutes {} seconds".format(timer["total_hours"], timer["total_minutes"], timer["total_seconds"]))

    # reset timer
    def reset_timer(self, timer_index):
        timer = self.timers[timer_index]
        timer["total_hours"] = 0
        timer["total_minutes"] = 0
        timer["total_seconds"] = 0
        self.total_labels[timer_index].config(text="Total working time: 0 hours 0 minutes 0 seconds")
    
    # remove timer
    def remove_timer(self, timer_frame):
        print ("removing timer ", timer_frame ) 
        i=0
        for timer in self.timers:
            if timer["frame"] == timer_frame:
                timer_frame.destroy()
                self.timers.remove(timer)
                del self.timer_labels[i]
                break
            i+=1
        self.save_configuration()
        #self.load_configuration()
    
    # reset all timers
    def reset_all_timers(self):
        for i in range(len(self.timers)):
            self.reset_timer(i)

    def update_elapsed_time(self):
        for i, timer in enumerate(self.timers):
            if timer["tracking"]:
                elapsed_time = datetime.datetime.now() - timer["start_time"]
                offset=datetime.timedelta(0,0,0)
                if timer["total_hours"] != 0 or timer["total_minutes"] != 0 or timer["total_seconds"] != 0:
                    #values exist, so offset must be calculated and added to elapsed time
                    offset = datetime.timedelta(hours=timer["total_hours"],minutes=timer["total_minutes"],seconds=timer["total_seconds"])
                    timer["start_time"] = datetime.datetime.now()
                elapsed_time+=offset
                hours, remainder = divmod(elapsed_time.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                                
                timer["total_hours"] = int(hours)
                timer["total_minutes"] = int(minutes)
                timer["total_seconds"] = int(seconds)

                #timer["start_time"] = datetime.datetime.now()
                self.total_labels[i].config(text="Total working time: {} hours {} minutes {} seconds".format(timer["total_hours"], timer["total_minutes"], timer["total_seconds"]))
        self.master.after(1000, self.update_elapsed_time)


    def create_timer_widgets(self):
        for i, timer in enumerate(self.timers):
            timer_frame = tk.Frame(self.master)
            timer_frame.pack()

            timer_label = self.timer_labels[i]
            timer_label.pack(side=tk.LEFT)

            action_button = self.action_buttons[i]
            action_button.pack(side=tk.LEFT)

            total_label = self.total_labels[i]
            total_label.pack(side=tk.LEFT)

            reset_button = self.reset_buttons[i]
            reset_button.pack(side=tk.LEFT)
            
            remove_button = self.remove_buttons[i]
            remove_button.pack(side=tk.LEFT)
   

    def start(self):
        print("entering start(self)")
        self.create_timer_widgets()
        self.update_elapsed_time()
        #self.master.after(1000, self.update_elapsed_time)
        # Save configuration before closing
        self.master.protocol("WM_DELETE_WINDOW", self.save_configuration_and_quit)
        



if __name__ == "__main__":
    print("if __name__ == __main__:")
    root = tk.Tk()
    tracker = WorkingHoursTracker(root)
    tracker.start()
    root.mainloop()
