#!/usr/bin/env python3

from kivy.uix.checkbox import CheckBox
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from playsound import playsound
from datetime import datetime, timedelta
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
import time
"""
from demo_opts import get_device
from luma.core.render import canvas
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
"""
from PIL import ImageFont, ImageDraw

Builder.load_file("main.kv")

win_x = 800
win_y = 480
beepBool = None
#global sliderVal 
sliderVal = 15
startTime = 0
pauseTime = 0
lastPause = 0
Window.size = (win_x, win_y)
Window.fullscreen = False
#from kivy.config import Config
#Config.set('graphics', 'width', '800')
#Config.set('graphics', 'height', '480')

#oled
"""
serial = i2c(port=1, address=0x3D)
device = ssd1306(serial)
padding = 2
shape_width = 20
top = padding
bottom = device.height - padding - 1
"""


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
        

        self.time_slider = Slider(min=10, max=15, value=15, step=1,
                                  value_track=True, value_track_color=[1, 0, 0, 1], size_hint=[1, 0.5])

        self.slider_value = Label(
            text=str(self.time_slider.value), font_size="20dp", size_hint=[1, 0.5])

    def setSliderVal(self, val):
        self.sliderVal = val
    
    #def getSliderVal(self):
     #   return self.time_slider.value


    # Piepton nach eingestellter Zeit
    def beep(self):
        self.exam_dur = sliderVal  # Pruefungsdauer
        if self.number >= self.exam_dur+1:
            if self.init == 0:
                for _ in range(3):
                    playsound("data/beep.mp3")

                self.init = 1

    """
    def update_oled(self):
        with canvas(device) as draw:
            #draw.text((0, 0), self.timestr, fill="white")
            font = ImageFont.truetype('./fonts/Volter__28Goldfish_29.ttf', 44)
            draw.text((0, (64-44)/2), self.timestr,
                      fill="white", font=font, anchor="center")
    """

    # Timer
    def increment_time(self, interval):
        self.number += .1
        global startTime, pauseTime
        duration = time.time() - startTime + pauseTime
        #s = self.number
        s = int(duration)
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.timestr = '{:02}:{:02}'.format(
            int(minutes), int(seconds))
        """
        self.update_oled()
        """
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
            print (pauseTime)


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
        """
        self.update_oled()
        """
        self.init = 0

    # slider value
    def slider_chng(self, instance, value):
        self.slider_value.text = str(instance.value)
        global sliderVal
        sliderVal = instance.value


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


class ExampleApp(App):
    def build(self):
        return MainWidget()

ExampleApp().run()
