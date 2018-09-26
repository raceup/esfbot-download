# !/usr/bin/python3
# coding: utf_8

import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from hal.internet.selenium import SeleniumForm
from hal.internet.parser import html_stripper


PATH_TO_THIS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
PATH_TO_CHROMEDRIVER = os.path.join(PATH_TO_THIS_DIRECTORY, "chromedriver")  # to proper work with selenium
OUTPUT_FOLDER = os.path.join(PATH_TO_THIS_DIRECTORY, "esf", str(int(time.time())))
BROWSER_WAIT_TIMEOUT_SECONDS = 2


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

    def parse(self, browser):
        """
        :param browser: webdriver
            Browser to use.
        :return: void
            Parse raw html table and save results
        """

        def get_show_functions():
            """
            :return: list
                Get javascript methods to open esf sections and return table data
            """

            data = []  # output table that contain all values from html table
            for row in self.table.find_all("tr"):  # cycle through all rows
                row_items = []  # array of elements of this row
                for column_label in row.find_all("th"):
                    row_items.append(html_stripper(column_label.text))

                for column in row.find_all("td"):  # cycle through all columns
                    try:
                        show_function = column.a["onclick"].split(";")[0]  # remove return statement
                        self.show_functions.append(show_function)
                    except:
                        pass
                    row_items.append(html_stripper(column.text))  # get new table entry
                data.append(row_items)  # append row

            return data

        print("\t", self.name)  # debug only
        data = get_show_functions()
        for show_function in self.show_functions:  # if there are hidden tables to show
            browser.execute_script(show_function)
            inner_data = self.parse_inner_table(browser)  # get data from table
            data.append([])  # to show there is a inner table
            for row in inner_data:
                data.append(row)  # add to table data

        self.data = data

    @staticmethod
    def parse_inner_table(browser):
        """
        :param browser: webdriver
            Browser to use.
        :return: list of list
            Raw html table to 2D matrix
        """

        table = BeautifulSoup(browser.page_source, "html.parser").find_all("fieldset")[0]  # find database
        title = html_stripper(table.find_all("h3")[0].text)  # find title
        table = table.find_all("table", {"class": "overview"})[0]  # find table
        data = [[title]]  # add name of section
        for row in table.find_all("tr"):  # cycle through all rows
            data_row = []
            for column_label in row.find_all("th"):  # cycle through all labels
                data_row.append(
                    html_stripper(column_label.text)
                )

            for column in row.find_all("td"):  # cycle through all columns
                data_row.append(
                    html_stripper(column.text)
                )

            data.append(data_row)
        return data


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
                html_stripper(sections_title[i].text),  # find title
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
                ESFForm(
                    html_stripper(name),
                    html_stripper(status),
                    html_stripper(show_function)
                )
            )  # append just found element
        return esf_list


class FSGermanyLogin(object):
    """ Bot to perform login in FSG webpage """

    LOGIN_URL = "https://www.formulastudent.de/l/?redirect_url=%2F"

    def __init__(self, browser, user, password):
        """
        :param browser: webdriver
            Browser to use.
        :param user: string
            Username to perform login
        :param password: string
            User password to perform login
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
        SeleniumForm.fill_login_form(self.browser,
                                      self.user, "user",
                                      self.password, "pass")  # fill login form
        SeleniumForm.submit_form(self.browser, "submit")  # press login button
        WebDriverWait(self.browser, BROWSER_WAIT_TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.ID, "c2106"))
        )  # wait until fully loaded


class FSGermanyBot(object):
    """ Bot to navigate through Formula Student Germany webpage"""

    def __init__(self):
        object.__init__(self)

        self.browser = webdriver.Chrome(PATH_TO_CHROMEDRIVER)

    def login(self, user, password):
        """
        :param user: string
            Username to perform login
        :param password: string
            User password to perform login
        :return: void
            Login in FSG website.
        """

        bot = FSGermanyLogin(self.browser, user, password)  # create bot for login
        bot.login()  # perform login

    def get_esf_to_csv(self):
        """
        :return: void
            ESF form to .csv format
        """

        if not os.path.exists(OUTPUT_FOLDER):  # create output directory
            os.makedirs(OUTPUT_FOLDER)

        bot = ESFSraper(self.browser)
        esf_list = bot.get_esf_list()
        for esf in esf_list:
            esf.get_sections(self.browser)  # get all sections of form
            out_filename = os.path.join(OUTPUT_FOLDER, esf.name + ".csv")
            with open(out_filename, "w") as o:
                for section in esf.sections:
                    section_csv = "\"" + str(section.name) + "\"" + "\n"  # add name of section
                    for row in section.data:
                        row_csv = ""
                        for value in row:
                            row_csv += "\"" + str(value) + "\"" + ","  # create a .csv row with " as text delimiter
                        section_csv += row_csv + "\n"  # add just created row
                    section_csv += "\n"
                    o.write(section_csv + "\n")  # write all sections of form

    def get_all_esf_to_csv(self, items):
        """
        :param items: list
            list of int, each int is the item to download the esf of
        :return: void
            All ESF forms to .csv format
        """

        def close_alert_in_time(driver, max_time):
            """
            :param driver: selenium web driver
                web driver to use
            :param max_time: int
                Max seconds to wait for alert
            :return: void
                Close all alerts popping up in max_time seconds interval
            """

            max_time_wait = time.time() + max_time
            is_alert_dismissed = False
            while time.time() < max_time_wait and not is_alert_dismissed:
                if is_alert_dismissed:  # can exit loop
                    break
                try:
                    driver.switch_to.alert.accept()  # discard any pop-up
                    is_alert_dismissed = True
                except:
                    time.sleep(0.2)
        
        if not os.path.exists(OUTPUT_FOLDER):  # create output directory
            os.makedirs(OUTPUT_FOLDER)

        bot = ESFSraper(self.browser)
        esf_form = bot.get_esf_list()[0]  # get an esf form: it's the same with the others

        self.browser.execute_script(esf_form.show_function)  # go to page of esf form
        WebDriverWait(self.browser, BROWSER_WAIT_TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.NAME, "submit"))
        )  # wait until fully loaded

        for i in items:  # loop through functions to execute
            out_filename = os.path.join(OUTPUT_FOLDER, str(i) + ".csv")  # file to write output
            javascript_function_to_show_item = "showItem(" + str(i) + ");"  # js function to open esf table
            print("Getting item ", i)

            data = []  # data of table
            self.browser.execute_script(javascript_function_to_show_item)  # open table
            close_alert_in_time(self.browser, BROWSER_WAIT_TIMEOUT_SECONDS)

            try:
                print("Parsing item ", i)
                inner_data = ESFFormSection.parse_inner_table(self.browser)  # get data from table
                for row in inner_data:
                    data.append(row)  # add to table data

                with open(out_filename, "w") as o:  # write output file
                    section_csv = "\"" + str(i) + "\"" + "\n"  # add name of section
                    for row in data:
                        row_csv = ""
                        for value in row:
                            row_csv += "\"" + str(value) + "\"" + ","  # create a .csv row with " as text delimiter
                        section_csv += row_csv + "\n"  # add just created row
                    section_csv += "\n"
                    o.write(section_csv + "\n")  # write all sections of form
            except:
                print("Failed getting item ", i)

    def exit(self):
        self.browser.close()
