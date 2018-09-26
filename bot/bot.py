# !/usr/bin/python3
# coding: utf_8

import argparse

from esfbot.fsg import fsg
from esfbot.fsg import crawler


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(usage="-u <user to login to FSG website> -p <password to login to FSG website>")
    parser.add_argument("-u", dest="user", help="user to login to FSG website", required=True)
    parser.add_argument("-p", dest="password", help="password to login to FSG website", required=True)
    return parser


def parse_args(parser):
    """
    :param parser: ArgumentParser
        Object that holds cmd arguments.
    :return: tuple
        Values of arguments.
    """

    args = parser.parse_args()
    return str(args.user), str(args.password)


def get_login_credentials():
    """
    :return: tuple string, string
        user, password
    """

    return parse_args(create_args())  # get credentials from command line


if __name__ == "__main__":
    user, password = get_login_credentials()  # get credentials
    bot = fsg.FSGermanyBot()  # bot to scrape

    print("Logging in...")
    bot.login(user, password)  # login to access members-only data

    crawler.download_all_esf(bot)
