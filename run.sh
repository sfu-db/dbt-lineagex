#!/bin/sh

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
pip install -r $SCRIPT_DIR/scripts/requirements.txt
python3 $SCRIPT_DIR/scripts/main.py
