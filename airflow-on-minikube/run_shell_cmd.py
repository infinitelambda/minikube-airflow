import subprocess
from subprocess import check_output, CalledProcessError

def run_shell_command(*commands):
    commands = [' \n'.join(commands)][0]
    try:
        cmd_output = check_output(
            commands,
            stderr=subprocess.STDOUT,
            shell=True
        )
        cmd_output = cmd_output.decode("utf-8")
        print(cmd_output)
    except CalledProcessError as cpe:
        print('**** Error calling cmd ****')
        print(cpe)
        print('**** STDERR + STDOUT **** ')
        for line in str(cpe.stderr).split('\\n'):
            print("stderr")
            print(line)
        for line in str(cpe.stdout).split('\\n'):
            print("stdout")
            print(line)
        raise cpe