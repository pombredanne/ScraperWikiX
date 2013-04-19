#!/bin/bash
if [ -z "$VIRTUAL_ENV" ]; then
    echo "You need to run this install a virtualenv"
    exit 1
fi

pip install -r install/requirements.txt

echo "Go and install node from http://nodejs.org/download/"
# Not tested yet
#wget http://nodejs.org/dist/v0.10.4/node-v0.10.4.tar.gz
#mv node-v0.10.4.tar.gz build
#cd build
#tar -xzvf node-v0.10.4.tar.gz
#cd node-v0.10.4
#./configure
#make
#echo "Need to authenticate to install node and run ''"
#sudo make install

npm install mu opts streamlogger underscore
