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
from hal.files import models


DIRECTORY = "/home/stefano/Coding/Python/misc/misc/web/fsgermany/esf/"
out_filename = os.path.join(DIRECTORY, "esf.csv")
out_data = ""
files = models.Directory().ls(DIRECTORY, False)  # get list of files
for f in files:
    directory, name = manager.extract_path_name(f)
    name = name.replace(".csv", "")
    data = open(f).read()
    print(name)
    out_data += "\"" + str(name) + "\"" + "\n"  # .csv
    out_data += data + "\n\n"

with open(out_filename, "w") as o:
    o.write(out_data)
