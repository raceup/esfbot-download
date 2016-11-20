# !/usr/bin/python
# coding: utf_8

# Copyright 2016 Stefano Fogarollo
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import sys
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

""" Scrape FSG data in a pythonic way. """

path_to_this_directory = os.path.realpath(__file__)
path_to_this_directory = path_to_this_directory[0: path_to_this_directory.rfind("/")]
PATH_TO_CHROMEDRIVER = os.path.join(path_to_this_directory, "chromedriver")  # to proper work with selenium
OUTPUT_FOLDER = "/home/stefano/Coding/Python/misc/misc/web/fsgermany/esf/"
BROWSER_WAIT_TIMEOUT_SECONDS = 5


class SeleniumUtils:
    """ Great and simple static methods to deal with selenium webdrivers. """

    @staticmethod
    def strip_raw_html_string(string):
        """
        :param string: string
            String to parse
        :return: string
            Given string with raw HTML elements removed
        """

        out = string.replace("\n", "") \
            .replace("\r", "") \
            .replace("\t", "") \
            .strip()

        while out.find("  ") > 0:  # while there are multiple blanks in a row
            out = out.replace("  ", " ")
        return out.encode("utf-8")

    @staticmethod
    def fill_form_field(browser, field_name, field_value):
        """
        :param browser: webdriver
            Browser to use to submit form.
        :param field_name :string
            Name of field to fill
        :param field_value: string
            Value with which to fill field.
        :return: void
            Fill given field wiht given value.
        """

        browser.execute_script(
            "document.getElementsByName(\"" + str(field_name) + "\")[0].value = \"" + str(field_value) + "\"")

    @staticmethod
    def fill_login_form(browser, username, username_field, userpassword, userpassword_field):
        """
        :param browser: webdriver
            Browser to use to submit form.
        :param username: string
            Username of user to login.
        :param username_field: string
            Name of field to fill with username.
        :param userpassword: string
            Password of user to login.
        :param userpassword_field: string
            Name of field to fill with userpassword.
        :return: void
            Form filled with given information.
        """

        SeleniumUtils.fill_form_field(browser, username_field, username)  # set username
        SeleniumUtils.fill_form_field(browser, userpassword_field, userpassword)  # set password

    @staticmethod
    def submit_form(browser, button_name):
        """
        :param browser: webdriver
            Browser to use to submit form.
        :param button_name: string
            Name of button to press to submit form
        :return: void
            Submit form.
        """

        browser.execute_script("document.getElementsByName(\"" + button_name + "\")[0].click()")  # click button


class ESFFormSection(object):
    """ Chapter of an ESF form """

    def __init__(self, name, table):
        """
        :param name: string
            Name of chapter
        :param table: soup
            Beautifusoup wrapper for raw html table
        """

        object.__init__(self)

        self.name = name
        self.table = table
        self.data = None
        self.show_functions = []  # javascript show methods to show extra data

    def parse_inner_table(self, browser):
        """
        :param browser: webdriver
            Browser to use.
        :return: list of list
            Raw html table to 2D matrix
        """

        fully_loaded = False
        while not fully_loaded:  # wait until fully loaded
            try:
                field_set = BeautifulSoup(browser.page_source, "html.parser").find_all("fieldset")[0]
                fully_loaded = True
            except:
                pass
            time.sleep(BROWSER_WAIT_TIMEOUT_SECONDS / 100)
        table = BeautifulSoup(browser.page_source, "html.parser").find_all("fieldset")[0]  # find database
        title = SeleniumUtils.strip_raw_html_string(table.find_all("h3")[0].text)  # find title
        table = table.find_all("table", {"class": "overview"})[0]  # find table
        data = [[title]]  # add name of section
        for row in table.find_all("tr"):  # cycle through all rows
            data_row = []
            for column_label in row.find_all("th"):  # cycle through all labels
                data_row.append(
                    SeleniumUtils.strip_raw_html_string(column_label.text)
                )

            for column in row.find_all("td"):  # cycle through all columns
                data_row.append(
                    SeleniumUtils.strip_raw_html_string(column.text)
                )

            data.append(data_row)
        return data

    def parse(self, browser):
        """
        :param browser: webdriver
            Browser to use.
        :return: void
            Parse raw html table and save results
        """

        print("\t", self.name)
        data = []  # output table that contain all valued from html table
        for row in self.table.find_all("tr"):  # cycle through all rows
            row_items = []  # array of elements of this row
            for column_label in row.find_all("th"):
                row_items.append(SeleniumUtils.strip_raw_html_string(column_label.text))

            for column in row.find_all("td"):  # cycle through all columns
                try:
                    show_function = column.a["onclick"].split(";")[0]  # remove return statement
                    self.show_functions.append(show_function)
                except:
                    pass
                row_items.append(SeleniumUtils.strip_raw_html_string(column.text))  # get new table entry
            data.append(row_items)  # append row

        for show_function in self.show_functions:  # if there are hidden tables to show
            browser.execute_script(show_function)
            inner_data = self.parse_inner_table(browser)  # get data from table
            data.append([])  # to show there is a inner table
            for row in inner_data:
                data.append(row)  # add to table data

        self.data = data


class ESFForm(object):
    """ ESF form in FSG webpage """

    def __init__(self, name, status, show_function):
        """
        :param name: string
            Name of form
        :param status: string
            Status of form
        :param show_function: string
            Javascript function to show form
        """

        object.__init__(self)

        self.name = name
        self.status = status
        self.show_function = show_function
        self.sections = None  # sections of form

    def get_sections(self, browser):
        """
        :param browser: webdriver
            Browser to use.
        :return: void
            Show this form.
        """

        print(self.name)
        browser.execute_script(self.show_function)  # go to page of esf form
        WebDriverWait(browser, BROWSER_WAIT_TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.NAME, "submit"))
        )  # wait until fully loaded
        soup = BeautifulSoup(browser.page_source, "html.parser")
        
        sections = []
        sections_title = soup.find_all("h3")[1:]  # discard first title
        sections_data = soup.find_all("table", {"class": "overview"})
        for i in range(len(sections_title)):  # cycle through all sections
            section = ESFFormSection(
                SeleniumUtils.strip_raw_html_string(sections_title[i].text),  # find title
                sections_data[i]  # find table
            )  # create section from raw data

            section.parse(browser)  # parse raw html
            sections.append(section)  # add just found section

        self.sections = sections
        browser.execute_script("window.history.go(-1)")  # back of one page in history to restore browser state


class ESFSraper(object):
    """ Scrape ESF from FSG webpage """

    ESF_URL = "https://www.formulastudent.de/esf"

    def __init__(self, browser):
        """
        :param browser: webdriver
            Browser to use.
        """

        object.__init__(self)

        self.browser = browser

    def get_esf_list(self):
        """
        :return: list of ESFForm
            ESFForm parsed from given raw html table
        """

        self.browser.get(ESFSraper.ESF_URL)  # go to list of ESFs

        soup = BeautifulSoup(self.browser.page_source, "html.parser")  # parse source page
        table = soup.find_all("table", {"class": "overview"})[0]
        esf_list = []
        rows = table.find_all("tr")[1:]  # find all rows
        for row in rows:
            name = row.find_all("th")[0].text
            status = row.find_all("td")[0].text
            show_function = row.find_all("td")[1].find_all("input")[0]["onclick"]
            esf_list.append(
                ESFForm(SeleniumUtils.strip_raw_html_string(name),
                        SeleniumUtils.strip_raw_html_string(status),
                        SeleniumUtils.strip_raw_html_string(show_function))
            )  # append just found element
        return esf_list


class FSGermanyLogin(object):
    """ Bot to perform login in FSG webpage """

    LOGIN_URL = "https://www.formulastudent.de/l/?redirect_url=%2F"

    def __init__(self, browser, user="moratoal", password="formulasae"):
        """
        :param browser: webdriver
            Browser to use.
        :param user: string
            Username to perform login
        :param password: string
            Userpassword to perform login
        """

        object.__init__(self)

        self.browser = browser
        self.user = user
        self.password = password

    def login(self):
        """
        :return: void
            Login in FSG website.
        """

        self.browser.get(FSGermanyLogin.LOGIN_URL)  # open login url
        SeleniumUtils.fill_login_form(self.browser,
                        self.user, "user",
                        self.password, "pass")  # fill login form
        SeleniumUtils.submit_form(self.browser, "submit")  # press login button
        WebDriverWait(self.browser, BROWSER_WAIT_TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.ID, "c2802"))
        )  # wait until fully loaded


class FSGermanyBot(object):
    """ Bot to navigate through Formula Student Germany webpage"""

    def __init__(self):
        object.__init__(self)

        self.browser = webdriver.Chrome(PATH_TO_CHROMEDRIVER)

    def login(self):
        """
        :param browser: webdriver
            Browser to use .
        :return: void
            Login in FSG website.
        """

        bot = FSGermanyLogin(self.browser)  # create bot for login
        bot.login()  # perform login

    def get_esf_to_csv(self):
        """
        :return: csv
            ESF form to .csv format
        """

        bot = ESFSraper(self.browser)
        esf_list = bot.get_esf_list()
        for esf in esf_list:
            esf.get_sections(self.browser)  # get all setions of form
            out_filename = os.path.join(OUTPUT_FOLDER, esf.name + ".csv")
            with open(out_filename, "wb") as o:
                for section in esf.sections:
                    section_csv = "\"" + str(section.name) + "\"" + "\n"  # add name of section
                    for row in section.data:
                        row_csv = ""
                        for value in row:
                            row_csv += "\"" + str(value) + "\"" + ","  # create a .csv row with " as text delimeter
                        section_csv += row_csv + "\n"  # add just created row
                    section_csv += "\n"
                    o.write(section_csv + "\n")  # write all sections of form

    def exit(self):
        self.browser.close()


def main():
    """ Main subroutine """

    bot = FSGermanyBot()
    print("Logging in...")
    bot.login()  # login to access members-only data
    print("Getting esf...")
    bot.get_esf_to_csv()  # save esf to .csv
    print("Done!")
    bot.exit()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\r[!] User requesting exit...\n%s" % sys.exc_info()[1])
    except Exception:
        print("\r[!] Unhandled exception occured...\n%s" % sys.exc_info()[1])
