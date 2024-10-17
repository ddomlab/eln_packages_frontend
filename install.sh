#!/bin/bash
# a script to install the module, doesn't do anything super special, just prompts for an api key
# TURN THIS INTO A BATCH FILE
working_dir = $(dirname $0)

if [ ! -f $working_dir/api_key ]; then
    echo "Input an API key"
    read apikey
    echo apikey > $working_dir/api_key
fi
git submodule init
git submodule update
conda env create -f $working_dir/environment.yml
