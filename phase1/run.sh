#!/bin/bash
# Run script for the todo application

cd "$(dirname "$0")"
python3.13 -m src "$@"
