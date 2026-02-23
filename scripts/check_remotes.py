import os
import subprocess

base_path = '/Users/kooshapari/temp-PRODVERCEL/485/'
for entry in os.listdir(base_path):
    entry_path = os.path.join(base_path, entry)
    if os.path.isdir(entry_path):
        git_path = os.path.join(entry_path, '.git')
        if os.path.isdir(git_path):
            try:
                output = subprocess.check_output(['git', '-C', entry_path, 'remote', '-v'], stderr=subprocess.STDOUT, text=True)
                if 'agslag' in output:
                    print(f"FOUND agslag in {entry_path}")
                    print(output)
            except Exception:
                pass
