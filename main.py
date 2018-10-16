#!/usr/bin/env python3

from kivy.uix.checkbox import CheckBox
from kivy.app import App
from kivy.lang import Builder
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

Builder.load_file("main.kv")


class MainWidget(BoxLayout):
    number = NumericProperty()
    timestr = StringProperty()

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        Clock.schedule_interval(self.increment_time, .1)
        self.increment_time(0)
        self.stop()
        self.beep()
        self.number = 0
        self.init = 0

        self.time_slider = Slider(min=10, max=15, value=10, step=1,
                                  value_track=True, value_track_color=[1, 0, 0, 1])

        self.slider_value = Label(text=str(self.time_slider.value))

    # Piepton nach eingestellter Zeit
    def beep(self):
        self.exam_dur = 25  # Pruefungsdauer
        if self.number >= self.exam_dur+1:
            if self.init == 0:
                for _ in range(3):
                    playsound("data/beep.mp3")

                self.init = 1

    # Timer
    def increment_time(self, interval):
        self.number += .1

        s = self.number
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.timestr = '{:02}:{:02}'.format(
            int(minutes), int(seconds))

        self.beep()

    # Start
    def start(self):
        Clock.unschedule(self.increment_time)
        Clock.schedule_interval(self.increment_time, .1)

    # Pause
    def pause(self):
        Clock.unschedule(self.increment_time)
        self.init = 0

    # Stop - Nullsetzen
    def stop(self):
        Clock.unschedule(self.increment_time)
        self.timestr = "00:00"
        self.init = 0

    def slider_chng(self, instance, value):
        self.slider_value.text = str(instance.value)

    def settings(self):
        layout = GridLayout(cols=3, orientation="vertical")
        time_lbl = Label(text="Pruefungsdauer", font_size="25dp")
        self.time_slider.bind(value=self.slider_chng)

        layout.add_widget(time_lbl)
        layout.add_widget(self.time_slider)
        layout.add_widget(self.slider_value)

        popup = Popup(title='Einstellungen',
                      content=layout,
                      size_hint=(None, None), size=(400, 400))

        popup.open()


class ExampleApp(App):
    def build(self):
        return MainWidget()

ExampleApp().run()