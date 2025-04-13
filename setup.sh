#!/bin/bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 -m venv $script_dir/venv
source $script_dir/venv/bin/activate
pip install -r $script_dir/requirements.txt
