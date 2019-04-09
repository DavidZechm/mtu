#!/usr/bin/env python

from kivy.uix.widget import Widget
from kivy.app import App
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.base import runTouchApp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


class dropDownMenu(GridLayout):
    def build(self):
        # create a dropdown with 10 buttons
        dropdown = DropDown()
        for index in range(10):
            btn = Button(text='Value %d' % index, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))

            dropdown.add_widget(btn)

        # create a big main button
        mainbutton = Button(text='Hello', size_hint=(None, None))
        mainbutton.bind(on_release=dropdown.open)

        dropdown.bind(on_select=lambda instance,
                      x: setattr(mainbutton, 'text', x))

        runTouchApp(mainbutton)


class MyApp(App):
    def build(self):
        return dropDownMenu()


if __name__ == '__main__':
    MyApp().run()
