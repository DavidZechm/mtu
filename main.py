#!/usr/bin/env python3

from PIL import ImageDraw, ImageFont
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.config import Config
from kivy.clock import Clock
from kivy.app import App
from datetime import datetime, timedelta
from kivy.uix.dropdown import DropDown
import time
raspberry = False


if raspberry:
    import RPi.GPIO as GPIO
    from demo_opts import get_device
    from luma.core.interface.serial import i2c
    from luma.core.render import canvas
    from luma.oled.device import ssd1306
    from playsound import playsound


Builder.load_file("main.kv")

win_x = 800
win_y = 480

# global Variables
startTime = time.time()
pauseTime = 0
lastPause = 0
duration = 0
examDuration = 15 * 60
buzzTime = 10 * 60
buzzerPin = 21
buzzed = False
paused = False

Window.size = (win_x, win_y)
Window.fullscreen = raspberry
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')


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
        self.dropDownMenu()
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

    def dropDownMenu(self):
        self.dropMenu = DropDown()
        tenBtn = Button(text="10")
        twelveBtn = Button(text="12")

        self.dropMenu.add_widget(tenBtn)
        self.dropMenu.add_widget(twelveBtn)

        mainBtn = Button(text="Settings", pos=(0, 0))
        mainBtn.bind(on_release=self.dropMenu.open)

        self.dropMenu.bind(on_select=lambda instance,
                           x: setattr(mainBtn, "text", x))

        print("place")
        self.add_widget(mainBtn)


class ExampleApp(App):
    def build(self):
        return MainWidget()


ExampleApp().run()
