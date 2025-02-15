# boot.py -- run on boot-up

import machine
import os

def run_script(script_path):
    # print(f"Trying to run script: {script_path}")
    if script_path in os.listdir():
        try:
            with open(script_path) as f:
                exec(f.read())
            # print(f"Script {script_path} executado com sucesso.")
        except Exception as e:
            print(f"Error while running script {script_path}: {e}")
    else:
        print(f"Script not found: {script_path}")

scripts = [
    'main.py'
]

# Execute cada script
for script in scripts:
    run_script(script)