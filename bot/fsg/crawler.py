# !/usr/bin/python3
# coding: utf_8

from hal.wrappers.methods import handle_exceptions


@handle_exceptions
def download_all_esf(bot):
    """
    :param bot: FSGermanyBot
        Authenticated bot
    :return: void
        Login to FSG website, goes to esf section, then download all esf files
    """

    print("Getting esf...")
    bot.get_all_esf_to_csv(range(3000, 4000))  # save esf to .csv

    print("Done!")
    bot.exit()


@handle_exceptions
def download_esf(bot):
    """
    :param bot: FSGermanyBot
        Authenticated bot
    :return: void
        Login to fsg and download all esf files of team
    """

    print("Getting esf...")
    bot.get_esf_to_csv()  # save esf to .csv

    print("Done!")
    bot.exit()
