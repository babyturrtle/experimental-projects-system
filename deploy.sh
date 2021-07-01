#!/bin/bash

if [ -d ".venv" ]
then
    source .venv/Scripts/activate
    pip install -r requirements.txt
    python wsgi.py
    start http://localhost:5000/projects
else
    python -m venv .venv
    source .venv/Scripts/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python wsgi.py
    start http://localhost:5000/projects
fi