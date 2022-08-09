#!/usr/bin/python
import requests
import json
import os
import sys
import jsondiff

print("Hello world")

#########################
# ENV VARIABLES
CONTROL_PLANE_URL=sys.argv[1]
print(CONTROL_PLANE_URL)
USERNAME=os.environ['API_USER'] #sys.argv[2]
print(USERNAME)
PASSWORD=os.environ['API_PASSWORD'] #sys.argv[3]
#print(PASSWORD)
#########################
# CONSTANTS
HEADER = {"Content-Type": "application/json"}
AUTH = (USERNAME, PASSWORD)
#########################