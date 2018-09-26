# !/usr/bin/python3
# coding: utf_8

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
