"""This file contains all the functions for the vpn connection."""

from os import chdir, listdir, mkdir, remove, system, popen, rename
from urllib.request import urlretrieve
from zipfile import ZipFile
from requests import get
from bs4 import BeautifulSoup
from os.path import expanduser
from time import sleep

__author__ = "Prabhakar Jha"
__copyright__ = "Copyright (c) 2018 Prabhakar Jha"
__credits__ = ["Prabhakar Jha"]
__license__ = "MIT License"
__version__ = "1.0.0"
__maintainer__ = "Prabhakar Jha"
__email__ = "findmebhanujha@gmail.com"


class Vpn():
    """Contains function connect_profile() to connect to the server."""

    def __init__(self, password=""):
        """It initialize the basic required class instances."""
        self.SELECTED_PROFILE = ""
        self.SELECTED_PROFILE_URL = ""
        self.USER_BOOK = "vpnbook"
        self.USER_KEYS = "vpnkeys"
        self.URL_VPNBOOK = "http://www.vpnbook.com"
        self.LIST_URL_VPNBOOK_PROFILES = \
            {"Europe": "http://www.vpnbook.com/free-openvpn-account/VPNBook.com-OpenVPN-Euro1.zip",
             "Europe2": "http://www.vpnbook.com/free-openvpn-account/VPNBook.com-OpenVPN-Euro2.zip",
             "US": "http://www.vpnbook.com/free-openvpn-account/VPNBook.com-OpenVPN-US2.zip",
             "Canada": "http://www.vpnbook.com/free-openvpn-account/VPNBook.com-OpenVPN-CA1.zip",
             "DE": "http://www.vpnbook.com/free-openvpn-account/VPNBook.com-OpenVPN-DE1.zip"}
        self.profile_dir = ".PROFILES"
        self.password_file = "credential.txt"
        self.desktop_path = expanduser("~/Desktop/../")
        self.basedir = ".myvpn"
        self.user_data_file = "data.txt"
        self.root_password = password
        self.process_ = ""

        # If there is old data then update it!!!!
        if self.old_data_exist() is True:
            # helps to select the profile selected by the user previously
            self.retrieve_data()

    def change_dir(self, level):
        """
        The function change_dir takes argument level.

        It then navigates to the directory according to the level specified.
        """
        if level == 1:
            # Move to desktop_path
            chdir(self.desktop_path)
        if level >= 2:
            # Move to basedir
            chdir(self.desktop_path)
            if self.basedir not in listdir("."):
                mkdir(self.basedir)
            chdir(self.basedir)
        if level == 3:
            # Move to profiles
            if self.profile_dir not in listdir("."):
                mkdir(self.profile_dir)
            chdir(self.profile_dir)

    def old_data_exist(self):
        """
        It checks if any old data is there.

        old_data_exist() -> returns True if old data exists.
        else returns False.
        """
        self.change_dir(2)
        if self.profile_dir not in listdir('.'):
            mkdir(self.profile_dir)
            chdir(self.profile_dir)
            return False
        chdir(self.profile_dir)
        return True

    def retrieve_data(self):
        """It reads data file and updates the program."""
        if self.user_data_file in listdir('.'):
            user_data = open(self.user_data_file, "r")
            # validate the data also if user modified we may face issues
            self.SELECTED_PROFILE = user_data.readline()
            self.SELECTED_PROFILE_URL = user_data.readline()
            user_data.close()

    def update_data_file(self):
        """It updates the data file with the current data."""
        self.change_dir(3)
        user_data = open(self.user_data_file, "w")
        user_data.write(self.SELECTED_PROFILE)
        user_data.write("\n")
        user_data.write(self.SELECTED_PROFILE_URL)
        user_data.write("\n")
        user_data.close()

    def download_profile(self):
        """
        Function downloads all the required files from the VpnBook server.

        Only the tcp port 80 file is saved and rest all deleted.
        """
        download_url = self.SELECTED_PROFILE_URL
        self.change_dir(3)
        try:
            urlretrieve(download_url, "tempfile")
        except Exception:
            # Popup for net connection needed!!
            return -1
        if "tempfile" in listdir('.'):
            zip_ref = ZipFile("tempfile", 'r')
            zip_ref.extractall(".")
            zip_ref.close()
            remove("tempfile")
            # keeping only port80 tcp
            list_files = listdir('.')
            for file_ in list_files:
                if file_.find("tcp80") > 0:
                    list_files.remove(file_)
                    rename(file_, self.SELECTED_PROFILE + "Jha" + ".ovpn")
                elif file_.find("Jha") > 0:
                    list_files.remove(file_)
            if "credentials.txt" in list_files:
                list_files.remove("credentials.txt")
            return 0

    def list_profiles(self):
        """
        It returns the list of profiles.

        It returns [-1] if there is no profile
        """
        self.change_dir(3)
        files = listdir(".")
        if len(files) < 2:
            return [-1]
        else:
            return files

    def remove_profiles(self):
        """It deletes all the profiles in the application's directory."""
        profiles = self.list_profiles()
        if profiles[0] == -1:
            # already no file
            pass
        else:
            self.change_dir(3)
            files = listdir(".")
            if len(files) < 2:
                # error nothing to delete!!!!
                # return -1
                pass
            else:
                files.remove(self.password_file)
                for file_ in files:
                    remove(file_)
                # !!!tell that its done
        self.SELECTED_PROFILE = ""
        self.SELECTED_PROFILE_URL = ""
        self.update_data_file()

    def update_password(self):
        """Function updates the password from the Vpnbook server."""
        self.change_dir(3)
        url = self.URL_VPNBOOK
        req = get(url)
        soup = BeautifulSoup(req.text, "lxml")
        op = str(soup.find_all("li", {"id": "openvpn"})[0])
        op = op[op.find("Password"):].replace("\n", "")
        password = op[op.find(":") + 2:]
        password = password[:password.find("<")]
        cred_file = open(self.password_file, "w")
        cred_file.write(self.USER_BOOK)
        cred_file.write("\n")
        cred_file.write(password)
        cred_file.close()
        self.update_data_file()

    # def select_profile(self):
    #     count = 0
    #     servers = self.LIST_URL_VPNBOOK_PROFILES.keys()
    #     for profile_name in servers:
    #         count += 1
    #     while True:
    #         selected_profile_count = int(input("Select any profile\n"))
    #         if selected_profile_count > len(self.LIST_URL_VPNBOOK_PROFILES)\
    #            or selected_profile_count < 0:

    #         else:
    #             self.SELECTED_PROFILE = list(servers)[selected_profile_count]
    #             self.SELECTED_PROFILE_URL = self.LIST_URL_VPNBOOK_PROFILES[self.SELECTED_PROFILE]
    #             self.download_profile()
    #             break

    def connect_profile(self):
        """It tries to connnect to the selected_profile server."""
        self.old_data_exist()
        self.change_dir(3)
        self.update_password()
        self.change_dir(3)
        try:
            system(("echo {} | sudo -S openvpn --remap-usr1 SIGTERM --config {}  --auth-user-pass {} &").format(self.root_password, self.SELECTED_PROFILE + "Jha.ovpn", self.password_file))
            sleep(22)
            # Now checking if we were successfull or not!!!
            self.process_ = popen("ps -a | grep openvpn").read().\
                splitlines()[-1].split()[0]
            return 0
        except IndexError:
            # NO PID'S FOUND!!! Unable to connect!
            return -1

    def disconnect(self):
        """If there exists any connection with server then it disconnect it."""
        if self.process_ != "":
            try:
                system("echo {} | sudo -S kill {}".format(self.root_password,
                                                          self.process_))
                self.process_ = ""
            except Exception:
                pass

    def on_destroy(self):
        """Disconnect the user and saves all data before the app is closed."""
        self.disconnect()
        self.update_data_file()
        # anything else if needed
