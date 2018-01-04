"""Application File, This file is the main file to run.

Usage python3 surfOnVpn
Dependencies in setup.py file
"""


from threading import Thread
from os import system, popen
import subprocess as sub
from vpn import Vpn
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen


Config.set('graphics', 'minimum_width', '570')
Config.set('graphics', 'minimum_height', '600')

__author__ = "Prabhakar Jha"
__copyright__ = "Copyright (c) 2018 Prabhakar Jha"
__credits__ = ["Prabhakar Jha"]
__license__ = "MIT License"
__version__ = "1.0.0"
__maintainer__ = "Prabhakar Jha"
__email__ = "findmebhanujha@gmail.com"

global settings_menu
aboutus = '[font=RobotoMono-Regular] Hey there, I am Prabhakar Jha.\n'\
          ' Young and passonate guy who loves to \n solve challengin problem.'\
          '\n This project was initiated to have a \n UI based proper free '\
          ' and open source VPN \n Software.\n This software is for '\
          ' educational purpose only.\n Any illegal use of this '\
          ' software is\n strictly prohibitted!. \n\n '\
          ' Contact me : [u]findmebhanujha@gmail.com [/u]\n[/font]'

contribute = '[font=RobotoMono-Regular]                Liked my work.\n'\
             ' Great! you can also contribute to this project \n at'\
             ' the following link.\n\n '\
             ' [u]https://github.com/prabhakar1998/SurfOnVpn\n[/u][/font]'

install_requirements = ""

report_issue = "[font=RobotoMono-Regular]Contact Developer: "\
               "[u]findmebhanujha@gmail.com[/u][/font]"

neeed_help = "[font=RobotoMono-Regular]Contact Developer: "\
             " [u]findmebhanujha@gmail.com[/u][/font]"

settings_menu = {
    "About Us": aboutus,
    "Contribute": contribute,
    "Install Requirements": install_requirements,
    "Report An Issue": report_issue,
    "Need Help": neeed_help}


class StartScreen(Screen):
    """Initial screen where the user gives root password."""

    def verify_password(self, password_arg):
        """Function verifies if the root password is correct or not."""
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
            op = popen("echo {} | sudo -S ifconfig".format(password)).read()
            if op == "":
                popup = Popup(title='Incorrect Password',
                              content=Label(markup=True,
                                            text='[i]Double check password and try again.[/i]'),
                              auto_dismiss=True,
                              size_hint=(None, None),
                              size=(540, 350))
                popup.open()
            else:
                self.parent.current = "SurfOnVpn"


class SurOnVpnLayout(Screen, GridLayout):
    """Main screen of the application and its related functions."""

    def update_screen(self, level):
        """
        Function updates the Status of connection on screen.

        Usage:
           update_screen(level):
           if level = -1 : Disconneted, level = 0 Connecting,
              level = 1 Connected, level = 2 Intalling
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
        elif level == 2:
            self.ids.status.text = "Installing Requirements"
            self.ids.connect_button.background_color = 1, 1, 0, 1
            self.ids.connecting_gif.opacity = 0
            self.ids.connect_button.text = "Installing...."

    def install_requirements(self):
        """It installs the openvpn."""
        if self.check_packages() == 0:
            popup = Popup(title='Requirements Already Satishfied',
                          content=Label(markup=True,
                                        text='[font=RobotoMono-Regular]Requirements Already Satishfied. \nTry connecting to any server...[/font]'),
                          auto_dismiss=True,
                          size_hint=(None, None),
                          size=(540, 350))
            popup.open()
        else:
            system("echo {} | sudo -S apt-get update".format(password))
            system("echo {} | sudo -S apt-get install openvpn".format(password))
            if self.check_packages() != 0:
                popup = Popup(title='Failed To Install',
                              content=Label(markup=True,
                                            text='Failed to intall\n Try running [u]sudo apt-get update[/u].'),
                              auto_dismiss=True,
                              size_hint=(None, None),
                              size=(540, 350))
                popup.open()
        self.update_screen(-1)

    def settings(self, text):
        """All the functions related to settings is here."""
        global settings_menu, password
        if text == "Install Requirements":
            Thread(target=self.install_requirements).start()
            self.update_screen(2)
            # check if installed if yes tell if not tell
        elif text != "Settings":
            popup = Popup(title=text,
                          content=Label(markup=True, text=settings_menu[text]),
                          auto_dismiss=True,
                          size_hint=(None, None),
                          size=(540, 350),
                          )
            popup.open()

    def connect(self):
        """Connecting to the selected profile."""
        global password
        self.vpn = Vpn(password)
        self.vpn.SELECTED_PROFILE = self.ids.spinner_id.text
        self.vpn.SELECTED_PROFILE_URL = self.vpn.\
            LIST_URL_VPNBOOK_PROFILES[self.vpn.SELECTED_PROFILE]
        status = self.vpn.download_profile()
        if status == -1:
            # No internet connection!!!
            popup = Popup(title='NO Internet Connection',
                          content=Label(text='Please Check If You Have A Working Internet Connection.'),
                          auto_dismiss=True,
                          size_hint=(None, None),
                          size=(540, 350))
            popup.open()
            self.update_screen(-1)
        else:
            if self.vpn.connect_profile() == -1:
                self.update_screen(-1)
                popup = Popup(title='Failed',
                              content=Label(text='Failed to connect. Try connecting with different server.'),
                              auto_dismiss=True,
                              size_hint=(None, None),
                              size=(540, 350))
                popup.open()
            else:
                self.update_screen(1)

    def check_packages(self):
        """
        It Checks if the requirements are satishfied.

        The application requires the OpenVpn so if its not installed then the
        installation information is provided to user.
        """
        process = sub.Popen(["dpkg", "-s", "openvpn"],
                            stdout=sub.PIPE, stderr=sub.PIPE)
        output, errors = process.communicate()
        output = output.decode('utf-8')
        for i in output.splitlines():
            if "Status" in str(i):
                if "installed" in str(i):
                    return 0

    def connect_button(self, value):
        """It gets executed when the connect button is clicked."""
        if value == "Connect":
            # currently disconnected ...
            if self.check_packages() == 0:
                if self.ids.spinner_id.text == "Select Server":
                    popup = Popup(title='Oops, You are here!',
                                  content=Label(
                                        text='Please Select Any Server!!'),
                                  auto_dismiss=True,
                                  size_hint=(None, None),
                                  size=(540, 350))
                    popup.open()
                else:
                    self.update_screen(0)
                    Thread(target=self.connect).start()
            else:
                popup = Popup(title='Requirements Missing',
                              content=Label(text='Go to settings and click on Install Requirements'),
                              auto_dismiss=True,
                              size_hint=(None, None),
                              size=(540, 350))
                popup.open()
        elif value == "Connecting...":
            pass
        elif value == "Disconnect":
            self.vpn.disconnect()
            self.update_screen(-1)


class ScreenManagement(ScreenManager):
    """It helps in the transition from StartScreen to SurOnVpnLayout."""

    pass


presentation = Builder.load_file('surfOnVpn.kv')


class Application(App):
    """Application initializer class."""

    def build(self):
        """Initializing app."""
        self.title = "SurfOnVpn"
        self.icon = "setting.png"
        return presentation


app = Application()
app.run()
