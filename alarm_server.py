import argparse
import functools
import queue
import time
import tkinter as tk
from threading import Thread
from tkinter import Entry, Label, StringVar
import multiprocessing

import playsound
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

time_queue = queue.Queue()

class CountDown(BaseModel):
    hour: str
    minute: str
    second: str

def create_alarm_app(sound_file: str):
  root = tk.Tk()
  root.geometry("600x500")
  root.title("Time Counter")

  hour=StringVar()
  minute=StringVar()
  second=StringVar()

  hour.set("00")
  minute.set("00")
  second.set("00")

  root.grid_columnconfigure((0,1,2), weight=1)
  hour_label = Label(root, text="HH", font=("Arial", 20))
  hour_entry= Entry(root, textvariable=hour, font=("Arial", 30), justify="center")
  hour_label.grid(row=0, column=0, pady=30)
  hour_entry.grid(row=1, column=0)

  minute_label = Label(root, text="MM", font=("Arial", 20))
  minute_entry= Entry(root, textvariable=minute, font=("Arial", 30), justify="center")
  minute_label.grid(row=0, column=1)
  minute_entry.grid(row=1, column=1)

  second_label = Label(root, text="SS", font=("Arial", 20))
  second_entry= Entry(root, textvariable=second, font=("Arial", 30), justify="center")
  second_label.grid(row=0, column=2)
  second_entry.grid(row=1, column=2)

  def set_countdown(count_down: CountDown):
    temp = int(count_down.hour)*3600 + int(count_down.minute)*60 + int(count_down.second)
    while temp >-1:
      if not time_queue.empty():
        return

      mins,secs = divmod(temp,60)
      hours=0
      if mins > 60:
        hours, mins = divmod(mins, 60)
      hour.set("{0:2d}".format(hours))
      minute.set("{0:2d}".format(mins))
      second.set("{0:2d}".format(secs))
      root.update()
      time.sleep(1)
      if (temp == 0):
        p = multiprocessing.Process(target=playsound.playsound, args=(sound_file, ))
        p.start()
        while p.is_alive():
          if not time_queue.empty():
            p.terminate()
          time.sleep(0.1)
      temp -= 1

  def check_queue():
    try:
      while True:
        new_time = time_queue.get_nowait()
        set_countdown(new_time)
    except queue.Empty:
      pass
    root.after(100, check_queue)

  root.after(100, check_queue)
  return root


web_app = FastAPI()

@web_app.post("/set_alarm/")
def set_alarm(count_down: CountDown):
  time_queue.put(count_down)

def run_web_app(host: str, port: int):
  uvicorn.run(web_app, host=host, port=port)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Run the alarm web api and UI.')
  parser.add_argument('--host', type=str, default="0.0.0.0", dest="host",
                      help='The web api host, default to 0.0.0.0')
  parser.add_argument('--port', type=int, default=8080, dest="port",
                      help='The web api port, default to 8080')
  parser.add_argument('--sound_file', type=str, required=True, dest='sound_file',
                      help='Sound to play when the count down hits zero')
  args = parser.parse_args()

  run_web_app_fn = functools.partial(
      run_web_app, host=args.host, port=args.port)

  api_thread = Thread(target=run_web_app_fn, )
  api_thread.start()

  alarm_app = create_alarm_app(args.sound_file)
  alarm_app.mainloop()
