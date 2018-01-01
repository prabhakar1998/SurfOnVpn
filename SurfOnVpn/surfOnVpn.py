"""
Application File, This file is the main file to run and it imports all other files.



"""
import os, threading
import subprocess as sub
from vpn import *
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.app import App


Config.set('graphics', 'minimum_width', '550')
Config.set('graphics', 'minimum_height', '600')

Builder.load_file('surfOnVpn.kv')


class CalcGridLayout(GridLayout):

    global aboutus
    aboutus = 'Hey there, I am Prabhakar Jha. Young and passonate guy '\
              'who loves to solve problem. This project was initiated to'\
              ' have a UI based proper free and open source VPN '\
              'Software. This software is meant for education purpose'\
              ' only. Any illegal use of this software is strictly '\
              'prohibitted!. Contact me: findmebhanujha@gmail.com'

    def updateScreen(self, level):
        """
        This function updates the Status of connection on screen.
        Usage:
           updateScreen(level):
             if level == -1 : Disconneted, level = 0 Connecting, level = 1 Connected
        """
        if level == -1:
            self.ids.status.text = "Disconnected"
            self.ids.connect_button.text = "Connect"
            self.ids.connecting_gif.opacity = 0
            self.ids.connect_button.background_color = 0, 1, 0, 1
        elif level == 0:
            self.ids.connecting_gif.opacity = 1
            self.ids.connect_button.text = "Connecting..."
            self.ids.connect_button.background_color = 204 / 225, 0,
        elif level == 1:
            self.ids.status.text = "Connected"
            self.ids.connect_button.background_color = 1, 0, 0, 1
            self.ids.connecting_gif.opacity = 0
            self.ids.connect_button.text = "Disconnect"

    def settings(self, text):
        # "Settings", "About Us", "Contribute", "Help", "Report Issue"
        global aboutus
        if text == "Settings":
            pass
        elif text == "About Us":
                popup = Popup(title='About Us',
                              content=Label(text=aboutus),
                              auto_dismiss=True,
                              size_hint=(None, None),
                              size=(540, 300))
                popup.open()

    def Connect(self):
        # connect here
        self.vpn = Vpn()
        self.vpn.SELECTED_PROFILE = self.ids.spinner_id.text
        self.vpn.SELECTED_PROFILE_URL = self.vpn.LIST_URL_VPNBOOK_PROFILES[self.vpn.SELECTED_PROFILE]
        # self.vpn.setAcess()
        status = self.vpn.download_profile()
        if status == -1:
            # No internet connection!!!
            popup = Popup(title='NO Internet Connection',
                          content=Label(text='Please Check If You Have A Working Internet Connection.'),
                          auto_dismiss=True,
                          size_hint=(None, None),
                          size=(540, 300))
            popup.open()
            self.updateScreen(-1)
        else:
            if self.vpn.connect_profile() == -1:
                self.updateScreen(-1)
                popup = Popup(title='Failed',
                              content=Label(text='Failed to connect'),
                              auto_dismiss=True,
                              size_hint=(None, None),
                              size=(540, 300))
                popup.open()
            else:
                self.updateScreen(1)

    def check_packages(self):
        process = sub.Popen(["dpkg", "-s", "openvpn"], stdout=sub.PIPE, stderr=sub.PIPE)
        output, errors = process.communicate()
        output = output.decode('utf-8')
        for i in output.splitlines():
            if "Status" in str(i):
                if "installed" in str(i):
                    return
        os.system("sudo apt-get install openvpn")

    def toggle(self, value):
        if value == "Connect":
            # currently disconnected ...
            self.check_packages()
            if self.ids.spinner_id.text == "Select Server":
                popup = Popup(title='Oops, You are here!',
                              content=Label(text='Please Select Any Server!!'),
                              auto_dismiss=True,
                              size_hint=(None, None),
                              size=(200, 200))
                popup.open()
            else:
                self.updateScreen(0)
                threading.Thread(target=self.Connect).start()
        elif value == "Connecting...":
            pass
        else:
            self.vpn.disconnect()
            self.updateScreen(-1)


class Application(App):
    def build(self):
        self.title = "SurfOnVpn"
        self.icon = "setting.png"
        return CalcGridLayout()

app = Application()
app.run()