#! /bin/bash

python3 ./modules/displayHostname.py &
jupyter-notebook --ip=0.0.0.0 --no-browser