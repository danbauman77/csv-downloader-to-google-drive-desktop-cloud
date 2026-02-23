#!/usr/bin/env python3

import os
import urllib.request

# ALGEBRA

FILE_URL = "https://www.aphis.usda.gov/sites/default/files/awa-hpa-actions.csv"

TARGET_DIR = "/Users/XXXX/My Drive/IFTTT/aphis_usda_gov_actions/csv"

# NEXT ...

os.makedirs(TARGET_DIR, exist_ok=True)

# DOWNLOAD

filename = os.path.basename(FILE_URL)
dest_path = os.path.join(TARGET_DIR, filename)

urllib.request.urlretrieve(FILE_URL, dest_path)