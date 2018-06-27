import libsonyapi
from libsonyapi import Actions
import tkinter as tk
from tkinter import messagebox
import threading
import time
import datetime


pylapse_font = ('Trebuchet', 14)

class CustomLabel(tk.Label):
    def __init__(self, parent, **kwargs):
        tk.Label.__init__(self, parent, **kwargs)
        self.config(font = pylapse_font)
        self.pack()
class PyLapse(tk.Tk):
    def __init__(self):
        super(PyLapse, self).__init__()
        self.title('PyLapse')

class MainScreen(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self,parent)
        tk.Label(self, text='PyLapse', font = ('Trebuchet', 20)).grid(row=1)
        self.set_live_view()
        self.set_timelapse_frame()

    def set_live_view(self):
        # TODO: implement live view, scrap controls
        live_view_frame = tk.Frame(self)
        live_view_frame.grid(row=2)

        live_view = tk.Frame(live_view_frame)
        live_view.grid(row=1, column=1)
        CustomLabel(live_view, text = 'live view')

        live_view_controls_frame = tk.Frame(live_view_frame)
        live_view_controls_frame.grid(row=1, column=2)
        CustomLabel(live_view_controls_frame, text = 'controls')

        self.camera_connect_button = tk.Button(live_view_frame, text='Connect to camera', font=pylapse_font,command = self.connect_to_camera)
        self.camera_connect_button.grid(row=2, column=1,columnspan=2)
        self.camera_connection_status = tk.Label(live_view_frame, font = pylapse_font)
        self.camera_connection_status.grid(row=3, column=1,columnspan=2)

    def set_timelapse_frame(self):
        timelapse_frame = tk.Frame(self)
        timelapse_frame.grid(row=3)

        timelapse_settings_frame = tk.Frame(timelapse_frame)
        timelapse_settings_frame.grid(row=1, column=1)
        CustomLabel(timelapse_settings_frame, text='TIMELAPSE SETTINGS')
        CustomLabel(timelapse_settings_frame, text='FPS')
        self.fps_scale = tk.Scale(timelapse_settings_frame, orient=tk.HORIZONTAL, from_=0, to = 60, sliderlength = 10, length = 150, tickinterval=10, command=self.update_timelapse_info)
        self.fps_scale.pack()
        self.fps_scale.set(24)
        CustomLabel(timelapse_settings_frame, text='Interval\n(max:10min 59sec)')
        interval_frame = tk.Frame(timelapse_settings_frame, pady=5)
        interval_frame.pack()
        self.min_between_shots = tk.Spinbox(interval_frame, from_=0, to = 10, width=2, font = pylapse_font, command =self.update_timelapse_info)
        self.min_between_shots.grid(row=1,column=1)
        min_label = tk.Label(interval_frame, text = 'min',font=pylapse_font)
        min_label.grid(row=1,column = 2)
        self.sec_between_shot = tk.Spinbox(interval_frame, from_=0, to=59, width=2, font = pylapse_font,command=self.update_timelapse_info)
        self.sec_between_shot.grid(row=1,column=3)
        self.sec_between_shot.delete(0)
        self.sec_between_shot.insert(0,5)
        sec_label = tk.Label(interval_frame, text = 'sec', font=pylapse_font)
        sec_label.grid(row=1,column=4)
        timelapse_duration_label = CustomLabel(timelapse_settings_frame, text='Timelapse Duration')
        timelapse_duration_frame = tk.Frame(timelapse_settings_frame)
        timelapse_duration_frame.pack()
        self.timelapse_duration_min = tk.Spinbox(timelapse_duration_frame, from_=0, to = 99, width=2, font = pylapse_font, command =self.update_timelapse_info)
        self.timelapse_duration_min.grid(row=1,column=1)
        timelapse_duration_min_label = tk.Label(timelapse_duration_frame, text='min', font=pylapse_font)
        timelapse_duration_min_label.grid(row=1,column=2)
        self.timelapse_duration_sec = tk.Spinbox(timelapse_duration_frame, from_=0, to = 59, width=2, font = pylapse_font, command =self.update_timelapse_info)
        self.timelapse_duration_sec.grid(row =1, column=3)
        self.timelapse_duration_sec.delete(0)
        self.timelapse_duration_sec.insert(0,10)
        timelapse_duration_sec_label = tk.Label(timelapse_duration_frame, text='sec', font=pylapse_font)
        timelapse_duration_sec_label.grid(row=1,column=4)

        timelapse_info_frame = tk.Frame(timelapse_frame)
        timelapse_info_frame.grid(row=1, column=2)
        CustomLabel(timelapse_info_frame, text = 'TIMELAPSE INFO')
        self.total_shots = CustomLabel(timelapse_info_frame, text = 'Total Amount of Shots: ', pady = 35)
        self.shoot_duration = CustomLabel(timelapse_info_frame, text = 'Total Shooting Time: ', pady = 35)
        # self.duration = CustomLabel(timelapse_info_frame, text = 'Timelapse Duration: ', pady = 6)

        self.update_timelapse_info()

        start_button = tk.Button(self, text = 'START TIMELAPSE', font=pylapse_font, command=self.confirm)
        start_button.grid(row=4)

    def connect_to_camera(self):
        try:
            self.camera_connection_status.config(text='Connecting to camera...')
            self.camera = libsonyapi.Camera()
            self.camera.do(Actions.startRecMode)
            self.camera_connection_status.config(text='Successfully connected to ' + self.camera.name)
            self.camera_connect_button.grid_forget()
        except ConnectionError:
            self.camera_connection_status.config(text='Connection to camera failed')

    def get_params(self):
        fps = int(self.fps_scale.get())
        min = int(self.min_between_shots.get())
        sec = int(self.sec_between_shot.get())
        timelapse_duration = int(self.timelapse_duration_min.get()) * 60 + int(self.timelapse_duration_sec.get())
        total_interval_in_sec = min * 60 + sec
        total_shots =  timelapse_duration * fps
        shoot_duration = total_shots * total_interval_in_sec

        return fps, min, sec, timelapse_duration, total_interval_in_sec, total_shots, shoot_duration

    def update_timelapse_info(self, event = None):
        fps, min, sec, timelapse_duration, total_interval_in_sec, total_shots, shoot_duration = self.get_params()

        # BUG: division by zero need to handle
        self.total_shots.config(text= 'Total Amount of Shots:\n' + str(total_shots) + ' shots')
        self.shoot_duration.config(text = 'Total Shooting Time:\n' + str(int(shoot_duration/60)) + ' min ' + str(shoot_duration%60) + ' sec')
        # self.duration.config(text= 'Timelapse Duration:\n' + str(total_shots / fps) + ' sec')
        # print(fps,min,sec)

    def confirm(self):
        fps, min, sec, timelapse_duration, total_interval_in_sec, total_shots, shoot_duration = self.get_params()
        confirm_box = messagebox.askyesno('Start timelapse??',
                'Do you want to start a timelapse with the following settings:\n\n' +
                str(fps) + ' FPS with a ' +
                str(min) + ' min ' + str(sec) + ' sec interval' +
                ', which will make a ' + str(timelapse_duration) + ' second long timelapse\n\n' +
                'This timelapse will consist of ' + str(total_shots) + ' shots and will require ' +
                str(int(shoot_duration/60)) + ' min ' + str((shoot_duration%60)) + ' sec of total shooting time\n\n' +
                'Make sure you have set your camera to the desired settings!'
        )
        if confirm_box == True:
            #initizate timelapse
            timelapse = threading.Thread(target=self.start_timelapse, args=(total_interval_in_sec, total_shots))
            timelapse.daemon = True
            timelapse.start()

            self.top = tk.Toplevel(width=1000)
            self.top.title('Timelape in progress...')

            self.start_time = datetime.datetime.now()
            self.end_time = self.start_time + datetime.timedelta(seconds=shoot_duration)
            CustomLabel(self.top, text='Timelape in progress...')
            self.shot_count = CustomLabel(self.top)
            self.percent_done = CustomLabel(self.top)
            CustomLabel(self.top, text='-'*10)
            self.time_elapsed = CustomLabel(self.top)
            self.time_left = CustomLabel(self.top)
            time_started = CustomLabel(self.top, text='Time Started: ' + self.start_time.strftime('%I:%M'))
            estimate_complete = CustomLabel(self.top, text='Estimated Time Completion: ' + self.end_time.strftime('%I:%M'))

            self.refresh_info_toplevel(total_interval_in_sec, total_shots, shoot_duration)
            self.top.mainloop()
            # info_window = threading.Thread(target=self.info_toplevel, args=(total_interval_in_sec, total_shots, shoot_duration))
            # info_window.daemon = True
            # self.shots_taken = 0
            # while self.shots_taken != total_shots:
            #     self.after(1000, func=info_window.start)

    def start_timelapse(self, interval_in_sec, total_shots):
        """
        starts timelapse with params: interval and total shots
        """
        print('starting timelapse', interval_in_sec, total_shots)
        self.shots_taken = 0
        while self.shots_taken != total_shots:
            print(self.camera.do(Actions.actTakePicture))
            time.sleep(interval_in_sec)
            # self.after(interval_in_sec*1000, func=self.camera.do(Actions.actTakePicture))
            self.shots_taken += 1

    def refresh_info_toplevel(self, interval_in_sec, total_shots, shoot_duration):
        """
        displays info about timelapse
        """
        #time elapsed, estimated time completion, time left, shots count, percent done
        # FIXME: bug with top level
        # while self.shots_taken != total_shots:
        if self.shots_taken < total_shots:
            fps, min, sec, timelapse_duration, total_interval_in_sec, total_shots, shoot_duration = self.get_params()
            print('ran info toplevel')
            self.shot_count.config(text='Shots: ' + str(self.shots_taken) + '/' + str(total_shots))
            self.percent_done.config(text='Percent Completed: '+ (str((self.shots_taken/total_shots)*100) + '%'))
            self.time_elapsed.config(text='Time Elapsed: ' + str(datetime.datetime.now() - self.start_time).split('.')[0])
            self.time_left.config(text='Time Left: ' + str(self.end_time - datetime.datetime.now()).split('.')[0])
            self.after(1000, self.refresh_info_toplevel, total_interval_in_sec, total_shots, shoot_duration)
            # time.sleep(1)



if __name__ == '__main__':
    root = PyLapse()
    MainScreen(root).pack()
    root.mainloop()
