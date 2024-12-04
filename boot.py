# boot.py -- run on boot-up

import machine
import os

def run_script(script_path):
    if script_path in os.listdir(os.path.dirname(script_path)):
        exec(open(script_path).read())
    else:
        print("Script não encontrado: ", script_path)

# Defina os caminhos para os scripts que você deseja executar
scripts = [
    '/detector/co2.py',
    '/flame.py'
]

# Execute cada script
for script in scripts:
    run_script(script)