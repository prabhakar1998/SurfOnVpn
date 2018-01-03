"""Application File, This file is the main file to run.

Usage python3 surfOnVpn
Dependencies in setup.py file
"""


from threading import Thread
import subprocess as sub
from vpn import Vpn
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen


Config.set('graphics', 'minimum_width', '550')
Config.set('graphics', 'minimum_height', '600')

__author__ = "Prabhakar Jha"
__copyright__ = "Copyright (c) 2018 Prabhakar Jha"
__credits__ = ["Prabhakar Jha"]
__license__ = "MIT License"
__version__ = "1.0.0"
__maintainer__ = "Prabhakar Jha"
__email__ = "findmebhanujha@gmail.com"

global settings_menu
aboutus = '[font=RobotoMono-Regular] Hey there, I am Prabhakar Jha.\n Young and '\
          ' passonate guy who loves to \n solve challengin problem.\n This project was initiated to'\
          ' have a \n UI based proper free and open source VPN \n'\
          ' Software.\n This software is for educational purpose'\
          ' only.\n Any illegal use of this software is\n strictly'\
          ' prohibitted!. \n\n Contact me : [u]findmebhanujha@gmail.com [/u]\n[/font]'

contribute = '[font=RobotoMono-Regular]                Liked my work.\n'\
             ' Great! you can also contribute to this project \n at'\
             ' the following link.\n\n [u]https://github.com/prabhakar1998/SurfOnVpn\n[/u][/font]'

install_requirements = ""

report_issue = "[font=RobotoMono-Regular]Contact Developer: [u]findmebhanujha@gmail.com[/u][/font]"

neeed_help = "[font=RobotoMono-Regular]Contact Developer: [u]findmebhanujha@gmail.com[/u][/font]"

settings_menu = {
    "About Us": aboutus,
    "Contribute": contribute,
    "Install Requirements": install_requirements,
    "Report An Issue": report_issue,
    "Need Help": neeed_help}


class StartScreen(Screen):

    def verifyPassword(self, password_arg):
        global password
        if password_arg == "":
            popup = Popup(title='No Password Entered',
                          content=Label(text="Please Enter The Password"),
                          auto_dismiss=True,
                          size_hint=(None, None),
                          size=(540, 350))
            popup.open()
        else:
            #  check for root password
            #  if the root password is correct then
            password = password_arg
            print(password)
            self.parent.current = "SurfOnVpn"


class SurOnVpnLayout(Screen, GridLayout):
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
        global settings_menu
        if text == "Install Requirements":
            # do the installation stuff
            pass
        elif text != "Settings":
            popup = Popup(title=text,
                          content=Label(markup=True, text=settings_menu[text]),
                          auto_dismiss=True,
                          size_hint=(None, None),
                          size=(540, 350),
                          )
            popup.open()

    def Connect(self):
        # connect here
        global password
        self.vpn = Vpn(password)
        print(self.vpn.root_password)
        self.vpn.SELECTED_PROFILE = self.ids.spinner_id.text
        self.vpn.SELECTED_PROFILE_URL = self.vpn.LIST_URL_VPNBOOK_PROFILES[self.vpn.SELECTED_PROFILE]
        # self.vpn.setAcess()
        print("105")
        status = self.vpn.download_profile()
        print("107")
        if status == -1:
            # No internet connection!!!
            popup = Popup(title='NO Internet Connection',
                          content=Label(text='Please Check If You Have A Working Internet Connection.'),
                          auto_dismiss=True,
                          size_hint=(None, None),
                          size=(540, 350))
            popup.open()
            self.updateScreen(-1)
        else:
            print("118")
            if self.vpn.connect_profile() == -1:
                print("120")
                self.updateScreen(-1)
                popup = Popup(title='Failed',
                              content=Label(text='Failed to connect. Try connecting with different server.'),
                              auto_dismiss=True,
                              size_hint=(None, None),
                              size=(540, 350))
                popup.open()
            else:
                print("129")
                self.updateScreen(1)

    def check_packages(self):
        """
        The application requires the OpenVpn so if its not installed then the 
        installation information is provided to user.
        """
        process = sub.Popen(["dpkg", "-s", "openvpn"], stdout=sub.PIPE, stderr=sub.PIPE)
        output, errors = process.communicate()
        output = output.decode('utf-8')
        for i in output.splitlines():
            if "Status" in str(i):
                if "installed" in str(i):
                    return 0

    def toggle(self, value):
        if value == "Connect":
            # currently disconnected ...
            if self.check_packages() == 0:
                if self.ids.spinner_id.text == "Select Server":
                    popup = Popup(title='Oops, You are here!',
                                  content=Label(text='Please Select Any Server!!'),
                                  auto_dismiss=True,
                                  size_hint=(None, None),
                                  size=(540, 350))
                    popup.open()
                else:
                    self.updateScreen(0)
                    Thread(target=self.Connect).start()
            else:
                popup = Popup(title='Requirements Missing',
                              content=Label(text='Go to settings and click on Install Requirements'),
                              auto_dismiss=True,
                              size_hint=(None, None),
                              size=(540, 350))
                popup.open()
        elif value == "Connecting...":
            pass
        else:
            self.vpn.disconnect()
            self.updateScreen(-1)


class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file('surfOnVpn.kv')


class Application(App):
    def build(self):
        self.title = "SurfOnVpn"
        self.icon = "setting.png"
        return presentation

app = Application()
app.run()