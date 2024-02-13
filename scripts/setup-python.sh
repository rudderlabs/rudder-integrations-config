#!/bin/bash
sudo apt-get update
sudo apt-get -y install python3-pip
pip3 --version
pip3 install requests
pip3 install jsonschema
pip3 install jsondiff
pip3 install black
