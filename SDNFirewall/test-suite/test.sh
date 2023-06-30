#!/bin/bash

# This line can be commented out if you are not using Gif for version control.
# git pull
# wait
# copy configure and sdn-firewall to testing dir.
cp ../configure.pol ./
cp ../sdn-firewall.py ./
./start-firewall.sh configure.pol
# wait for testing to cease before cleanup.
wait
./cleanup.sh