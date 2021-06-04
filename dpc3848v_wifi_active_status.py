#!/usr/bin/env python
#
# Copyright (c) 2021, James Cherti
# GitHub: https://github.com/jamescherti/python-dpc3848v
#
# Distributed under terms of the MIT license.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""Turn On / Off the WiFi of the WiFi Modem DPC3848V."""


import os
import sys
import warnings
warnings.filterwarnings("ignore")
# pylint: disable=wrong-import-position
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.expected_conditions \
    import presence_of_element_located
from selenium.webdriver.support.ui import WebDriverWait


MANAGE_24GHZ = True  # Manage 2.4 Ghz WiFi
MANAGE_5G = False  # Manage 5G WiFi


class ManageDPC3848V:
    """Control the 'Technicolor DPC3848V DOCSIS 3.0 Gateway'."""

    def __init__(self,
                 driver: WebDriver,
                 url: str,
                 username: str,
                 password: str,
                 wait_time : int = 30):
        """Login to the router web interface."""
        self.wait = WebDriverWait(driver, wait_time)
        self.driver = driver
        self.url = url

        self.driver.get(self.url)

        self.wait.until(
            presence_of_element_located((By.ID, "username_login"))
        ).send_keys(username)

        self.wait.until(
            presence_of_element_located((By.ID, "password_login"))
        ).send_keys(password)

        self.wait.until(
            presence_of_element_located(
                (By.XPATH, '//input[@type="submit" and @value="Log In"]')
            )
        ).click()

    def set_wifi_status(self,
                        wifi_enabled: bool,
                        manage_24ghz : bool = True,
                        manage_5g : bool = True):
        """Enable or disable wifi."""
        self.driver.get(self.url)

        self.wait.until(
            presence_of_element_located((By.XPATH, '//a[@href="WPS.php"]'))
        ).click()

        self.wait.until(
            presence_of_element_located((By.XPATH,
                                         '//a[@href="WRadioSettings.php"]'))
        ).click()

        self.wait.until(
            presence_of_element_located((By.ID, "wifi_enable_dis"))
        ).click()

        list_checkboxes = []
        if manage_24ghz:
            if wifi_enabled:
                list_checkboxes.append("wifi_enable_en")
            else:
                list_checkboxes.append("wifi_enable_dis")

        if manage_5g:
            if wifi_enabled:
                list_checkboxes.append("wifi_enable_en_5g")
            else:
                list_checkboxes.append("wifi_enable_dis_5g")

        for checkbox_id in list_checkboxes:
            self.wait.until(
                presence_of_element_located((By.ID, checkbox_id))
            ).click()

        if list_checkboxes:
            self.wait.until(
                presence_of_element_located((By.ID, "save"))
            ).click()


def main():
    """The program starts here."""
    print("[INFO] 2.4 Ghz WiFi managed: {}".format(MANAGE_24GHZ))
    print("[INFO] 5G WiFi managed: {}".format(MANAGE_5G))
    print()

    action = input("Action [on, off]: ")
    if action not in ["on", "off"]:
        print("Error: action should be 'on' or 'off'.".format(), file=sys.stderr)
        sys.exit(1)

    wifi_enabled = bool(action == "on")

    router_url = input("URL (e.g. http://192.168.0.1): ")
    username = input("User: ")
    password = input("Password: ")

    capabilities = webdriver.DesiredCapabilities.FIREFOX
    capabilities['marionette'] = True

    options = webdriver.FirefoxOptions()
    options.headless = True

    # proxy_ip_port = "127.0.0.1:3128"
    # capabilities['proxy'] = {
    #     "proxyType": "MANUAL",
    #     "httpProxy": proxy_ip_port,
    #     "ftpProxy": proxy_ip_port,
    #     "sslProxy": proxy_ip_port
    # }

    with webdriver.Firefox(options=options,
                           capabilities=capabilities,
                           service_log_path=os.path.devnull) as driver:
        router = ManageDPC3848V(driver=driver,
                                url=router_url,
                                username=username,
                                password=password,
                                wait_time=30)

        router.set_wifi_status(
            wifi_enabled=wifi_enabled,
            manage_24ghz=MANAGE_24GHZ,
            manage_5g=MANAGE_5G
        )

        print()
        if wifi_enabled:
            print("[SUCCESS] Wifi enabled.")
        else:
            print("[SUCCESS] Wifi disabled.")


if __name__ == '__main__':
    main()
