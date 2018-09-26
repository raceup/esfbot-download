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
