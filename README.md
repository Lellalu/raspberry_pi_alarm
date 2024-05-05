# raspberry_pi_alarm
## Getting start

In this project, we recommend that you use virturalenv of python:
```
python3 -m venv venv
source venv/bin/activate 
```
To install the dependencies and install the ecco6 package: 
```
pip3 install -r requirements.txt
```
To run the project:
```
python alarm_server.py --sound_file notification.mp3 
```

If you run the alarm server over SSH, and you want to play the sound on the remote server, you should run:
```
DISPLAY=:0 python alarm_server.py --sound_file notification.mp3
```
