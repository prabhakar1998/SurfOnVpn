"""
This file contains all the functions for the project.

Author:
License:
USage:

"""

from os import chdir, listdir, mkdir, remove, system, popen, rename
from urllib.request import urlretrieve
from zipfile import ZipFile
from requests import get
from bs4 import BeautifulSoup
import datetime
from os.path import expanduser
import subprocess
import sys
import time
import shlex


class Vpn():

    def __init__(self):
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
        # self.basedir = "/usr/share/"
        # self.appdir = "myvpn"
        self.desktop_path = expanduser("~/Desktop/../")
        self.basedir = ".myvpn"
        self.user_data_file = "data.txt"
        self.last_updated = "-1"
        self.__root_password = ""
        self.process_ = ""

        # If there is old data then update it!!!!
        if self.old_data_exist() is True:
            self.retrieve_data()

    def changeDir(self, level):
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
        self.changeDir(2)
        if self.profile_dir not in listdir('.'):
            mkdir(self.profile_dir)
            chdir(self.profile_dir)
            return False
        chdir(self.profile_dir)
        return True

    def retrieve_data(self):
        if self.user_data_file in listdir('.'):
            user_data = open(self.user_data_file, "r")
            # validate the data also if user modified we may face issues
            self.SELECTED_PROFILE = user_data.readline()
            self.SELECTED_PROFILE_URL = user_data.readline()
            self.last_updated = user_data.readline()
            if self.last_updated != -1:
                date = tuple(map(lambda a: int(a), self.last_updated.split()))
                self.last_updated = datetime.date(date[0], date[1], date[2])
            user_data.close()

    def update_data_file(self):
        self.changeDir(3)
        user_data = open(self.user_data_file, "w")
        user_data.write(self.SELECTED_PROFILE)
        user_data.write("\n")
        user_data.write(self.SELECTED_PROFILE_URL)
        user_data.write("\n")
        user_data.write(self.last_updated)
        user_data.close()

    def download_profile(self):
        download_url = self.SELECTED_PROFILE_URL
        self.changeDir(3)
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
        self.changeDir(3)
        files = listdir(".")
        if len(files) < 2:
            return [-1]
        else:
            return files

    def remove_profiles(self):
        profiles = self.list_profiles()
        if profiles[0] == -1:
            # already no file
            pass
        else:
            self.changeDir(3)
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
        self.last_updated = "-1"
        self.update_data_file()

    def update_password(self):
        self.changeDir(3)
        difference = str(datetime.date.today() - self.last_updated).split()
        if len(difference) > 1:
            if self.last_updated == "-1" or \
               int(str(datetime.date.today() - self.last_updated).split()[0]) >= 3:
                # If last update was few days before
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
                self.last_updated = str(datetime.datetime.now()).split()[0].replace("-", " ")
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
        self.old_data_exist()
        self.changeDir(3)
        self.update_password()
        self.changeDir(3)
        try:
            system(("echo {} | sudo -S openvpn --remap-usr1 SIGTERM --config {}  --auth-user-pass {} &").format(self.__root_password, self.SELECTED_PROFILE + "Jha.ovpn", self.password_file))
            time.sleep(22)
            # Now checking if we were successfull or not!!!
            self.process_ = popen("ps -a | grep openvpn").read().splitlines()[-1].split()[0]
            return 0
        except IndexError:
            # NO PID'S FOUND!!! Unable to connect!
            return -1

    def disconnect(self):
        if self.process_ != "":
            try:
                system("echo {} | sudo -S kill {}".format(self.__root_password, self.process_))
                self.process_ = ""
            except Exception:
                pass

    def on_destroy(self):
        # VERY VERY IMP !!!!
        # keep the process id and then do something like ctrl + c
        self.remove_all_profiles()
        self.update_data_file()
        # anything else if needed

    def setAcess(self):
        pass
        # self.old_data_exist()
        # path = self.basedir+"/" + self.appdir + "/PROFILES/"
        # chdir(path)
        # system("echo {} | sudo -S chmod 777 *".format(self.__root_password))



if __name__ == '__main__':

    # call init or display function!!
    vpn = Vpn()
    # vpn.setAcess()
    vpn.select_profile()
    vpn.connect_profile()
