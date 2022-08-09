#!/usr/bin/python

import json
import jsondiff
import os
import requests
import sys

print("Hello world")

#########################
# ENV VARIABLES
USERNAME=os.environ['API_USER'] #sys.argv[2]
print(USERNAME)
PASSWORD=os.environ['API_PASSWORD'] #sys.argv[3]
#print(PASSWORD)
#########################
# CONSTANTS
#HEADER = {"Content-Type": "application/json"}
#AUTH = (USERNAME, PASSWORD)
#########################
