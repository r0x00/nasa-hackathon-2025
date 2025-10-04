#!/bin/bash

# start the virtual environment
pipenv shell

# install the dependencies
pipenv install

# run the application
pipenv run python main.py