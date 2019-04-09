#!/usr/bin/env python3

from PIL import ImageDraw, ImageFont
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.settings import SettingsWithSpinner
from kivy.properties import NumericProperty, StringProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.config import Config
from kivy.clock import Clock
from kivy.app import App
from datetime import datetime, timedelta
from kivy.config import ConfigParser
import time
import json

raspberry = False
config = ConfigParser()
config.read('config.ini')

if raspberry:
    import RPi.GPIO as GPIO
    from demo_opts import get_device
    from luma.core.interface.serial import i2c
    from luma.core.render import canvas
    from luma.oled.device import ssd1306
    #from playsound import playsound


Builder.load_file("main.kv")

win_x = 800
win_y = 480

# global Variables
startTime = time.time()
pauseTime = 0
lastPause = 0
duration = 0
examDuration = 15 * 60
buzzTime = int(examDuration * 0.90)
buzzerPin = 21
buzzed = False
paused = False

Window.size = (win_x, win_y)
Window.fullscreen = raspberry
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')


settings_json = json.dumps([
    {
        "type": "title",
        "title": "WIFI-HotSpot:\nSSID: Maturauhr\nPSK: Maturauhr-123"
    },
    {
        "type": "options",
        "title": "Zeitdauer",
        "desc": "Dauer der Pruefung.",
        "section": "config",
        "key": "time",
        "options": ["10", "12", "15"]
    },
    {
        "type": "bool",
        "title": "Fullscreen",
        "section": "config",
        "key": "fullscreen"
    }
    
    ])



# OLED
if raspberry:
    serial = i2c(port=1, address=0x3D)
    device = ssd1306(serial)
    padding = 2
    shape_width = 20
    top = padding
    bottom = device.height - padding - 1

    # GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(buzzerPin, GPIO.OUT)


class MainWidget(BoxLayout):
    
    number = NumericProperty()
    timestr = StringProperty()
   

    # init
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        Clock.schedule_interval(self.increment_time, .1)
        self.increment_time(0)
        self.stop()
        self.number = 0
        self.started = False


    # Piepton nach eingestellter Zeit
    def beep(self):
        global duration, buzzTime, buzzed
        if duration >= buzzTime:
            if not buzzed:
                for _ in range(2):
                    # playsound("data/beep.mp3")
                    print("beep")
                    if raspberry:
                        GPIO.output(buzzerPin, GPIO.HIGH)
                        time.sleep(0.5)
                        GPIO.output(buzzerPin, GPIO.LOW)
                        time.sleep(0.5)
                buzzed = True

    def update_oled(self):
        if raspberry:
            with canvas(device) as draw:
                # draw.text((0, 0), self.timestr, fill="white")
                font = ImageFont.truetype('./fonts/arial.ttf', 50)
                draw.text((0, 0), self.timestr,
                          fill="white", font=font, anchor="center")
                global duration, examDuration
                lenght = 128*(duration/(examDuration))
                height = 10
                draw.rectangle((0, 64, lenght, 64-height),
                               outline="white", fill="white")

    # Timer
    def increment_time(self, interval):
        self.number += .1
        global startTime, pauseTime, duration
        duration = time.time() - startTime + pauseTime
        s = int(duration)
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.timestr = '{:02}:{:02}'.format(
            int(minutes), int(seconds))

        self.update_oled()
        self.beep()

    # Start
    def start(self):
        global paused
        if not self.started:
            global startTime
            startTime = time.time()
            self.started = True
        if paused:
            global pauseTime, lastPause
            pauseTime = pauseTime + (lastPause - time.time())
            paused = False

        Clock.unschedule(self.increment_time)
        Clock.schedule_interval(self.increment_time, .1)

    # Pause
    def pause(self):
        global lastPause, paused
        if not paused:
            Clock.unschedule(self.increment_time)
            lastPause = time.time()
            paused = True

    # Stop - Nullsetzen
    def stop(self):
        Clock.unschedule(self.increment_time)
        self.timestr = "00:00"
        self.update_oled()
        self.started = False
        global pauseTime, paused, buzzed
        buzzed = False
        pauseTime = 0
        paused = False



class ExampleApp(App):
    def build(self):
        self.settings_cls = MySettings
        return MainWidget()

    global config
    
    def build_settings(self, settings):
        settings.add_json_panel('Settings', config, data=settings_json)

    def on_config_change(self, config, section, key, value):
        if key == "fullscreen":
            print(value)
            if value == "0":
                Window.fullscreen = False
            elif value == "1":
                Window.fullscreen = True

        if key == "time":
            global examDuration, buzzTime
            examDuration = int(value) * 60
            buzzTime = int(examDuration * 0.90)

    def close_settings(self, settings=None):
        super(ExampleApp, self).close_settings(settings)

class MySettings(SettingsWithSpinner):
    pass

ExampleApp().run()
