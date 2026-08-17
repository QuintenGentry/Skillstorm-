To run the following python project you must run the following commands inside the Assignment 1 directory:

python -m venv support_api/.venv

support_api\.venv\Scripts\Activate.ps1

pip install -e .

python main.py

No input is required to run any of the files. 

if you wish to run the tests, run 

pip install -e ".[test]"

python -m pytest -q
