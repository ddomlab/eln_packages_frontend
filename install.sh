#!/bin/bash
# a script to install the module, doesn't do anything super special, just prompts for an api key
DIR = $(dirname $0)

if [ ! -f $DIR/api_key ]; then
    echo "Input an API key"
    read apikey
    echo apikey > $DIR/api_key
fi
git submodule init
git submodule update