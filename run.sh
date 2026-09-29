#!/bin/bash
cd "$(dirname "$0")"
pip install -r requirements.txt -q
python3 luna_launcher.py
