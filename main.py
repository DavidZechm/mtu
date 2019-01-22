#!/usr/bin/env python3

import time
from datetime import datetime, timedelta

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from PIL import ImageDraw, ImageFont

import RPi.GPIO as GPIO
from demo_opts import get_device
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from playsound import playsound

Builder.load_file("main.kv")

win_x = 800
win_y = 480
beepBool = None

#global Variables
startTime = 0
pauseTime = 0
lastPause = 0
duration = 0
examDuration = 15 * 60
buzzTime = 10 * 60
buzzerPin = 21
buzzed = False

Window.size = (win_x, win_y)
Window.fullscreen = True
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

#oled

serial = i2c(port=1, address=0x3D)
device = ssd1306(serial)
padding = 2
shape_width = 20
top = padding
bottom = device.height - padding - 1

# GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(buzzerPin,GPIO.OUT)


class MainWidget(BoxLayout):
    number = NumericProperty()
    timestr = StringProperty()

    #init
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        Clock.schedule_interval(self.increment_time, .1)
        self.increment_time(0)
        self.stop()
        self.beep()
        self.number = 0
        self.init = 0
        self.started = False
        
        """
        self.time_slider = Slider(min=10, max=15, value=15, step=1,
                                  value_track=True, value_track_color=[1, 0, 0, 1], size_hint=[1, 0.5])
        self.slider_value = Label(
            text=str(self.time_slider.value), font_size="20dp", size_hint=[1, 0.5])"""


    # Piepton nach eingestellter Zeit
    def beep(self):
        global duration, buzzTime, buzzed
        if duration >= buzzTime:
            if not buzzed:
                for _ in range(2):
                    # playsound("data/beep.mp3")
                    GPIO.output(buzzerPin,GPIO.HIGH)
                    time.sleep(0.5)
                    GPIO.output(buzzerPin,GPIO.LOW)
                    time.sleep(0.5)
                buzzed = True


    def update_oled(self):
        with canvas(device) as draw:
            #draw.text((0, 0), self.timestr, fill="white")
            font = ImageFont.truetype('./fonts/arial.ttf', 50)
            draw.text((0, 0), self.timestr,
                      fill="white", font=font, anchor="center")
            global duration, examDuration
            lenght = 128*(duration/(examDuration))
            height = 10
            draw.rectangle((0, 64, lenght, 64-height), outline="white", fill="white")


    # Timer
    def increment_time(self, interval):
        self.number += .1
        global startTime, pauseTime, duration
        duration = time.time() - startTime + pauseTime
        #s = self.number
        s = int(duration)
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.timestr = '{:02}:{:02}'.format(
            int(minutes), int(seconds))

        self.update_oled()
        self.beep()


    # Start
    def start(self):
        if not self.started:
            global startTime
            startTime = time.time()
            self.started = True
        else:
            global pauseTime, lastPause
            pauseTime = pauseTime + (lastPause - time.time())
            #print (pauseTime)


        Clock.unschedule(self.increment_time)
        Clock.schedule_interval(self.increment_time, .1)

    # Pause
    def pause(self):
        Clock.unschedule(self.increment_time)
        global lastPause
        lastPause = time.time()
        self.init = 0

    # Stop - Nullsetzen
    def stop(self):
        Clock.unschedule(self.increment_time)
        self.timestr = "00:00"
        self.update_oled()
        self.init = 0
        self.started = False
        global pauseTime
        pauseTime = 0

    """
    # slider value
    def slider_chng(self, instance, value):
        self.slider_value.text = str(instance.value)
        global examDuration
        examDuration = instance.value
    """
    """
    # settings
    def settings(self):
        layout = GridLayout(cols=3, orientation="horizontal")
        time_lbl = Label(
            text="Piepton:", font_size="25dp", size_hint=[1, 1])
        self.time_slider.bind(value=self.slider_chng)
        beep_chk = CheckBox()
        popup = Popup(title='Einstellungen',
                      content=layout,
                      size_hint=(None, None), size=(500, 400),
                      auto_dismiss=False)

        popup.open()

        # save settings, basically
        def closeSettings(self):           
            beepBool = beep_chk.active
            popup.dismiss()
            layout.clear_widgets()
            #print "EXIT"

        closePopup = Button(text="Close")
        closePopup.bind(on_press=closeSettings)

        layout.add_widget(closePopup)
        layout.add_widget(time_lbl)
        layout.add_widget(beep_chk)
        layout.add_widget(self.time_slider)
        layout.add_widget(self.slider_value)
    """

class ExampleApp(App):
    def build(self):
        return MainWidget()

ExampleApp().run()
