import json
import os
import re
import subprocess
import sys

from setup.cli import *
from setup.colorConsole import *


def print_header():
    header = """
    ###################################################
    #########       Raspi Captive Portal      #########
    #########   A Raspberry Pi Access Point   #########
    #########  & Captive Portal setup script  #########
    ###################################################
    """
    ColorPrint.print(cyan, header)


def check_super_user():
    print()
    ColorPrint.print(cyan, '▶ Check sudo')

    # Is root?
    if os.geteuid() != 0:
        print('You need root privileges to run this script.')
        print('Please try again using "sudo"')
        sys.exit(1)
    else:
        print('Running as root user, continue.')


def setup_access_point(config_data):
    print()
    ColorPrint.print(cyan, '▶ Setup Access Point (WiFi)')

    print('We will now set up the Raspi as Access Point to connect to via WiFi.')
    print('The following commands will execute as sudo user.')
    print('Please make sure you look through the file "./access-point/setup-access-point.sh"')
    print('first before approving.')
    answer = query_yes_no('Continue?', default='yes')

    if not answer:
        return sys.exit(0)

    hostapdconfigpath = "./access-point/hostapd.conf"
    with open(hostapdconfigpath, 'r') as f:
        filedata = f.read()

    filedata = re.sub(r'wpa_passphrase=.*',
                      f'wpa_passphrase={config_data["password"]}', filedata)
    filedata = re.sub(r'ssid=.*',
                      f'ssid={config_data["ssid"]}', filedata)

    with open(hostapdconfigpath, 'w') as f:
        f.write(filedata)

    accespointsh = "./access-point/setup-access-point.sh"
    with open(accespointsh, 'r') as f:
        filedata = f.read()

    filedata = re.sub(r'--to-destination 192.168.4.1:.*',
                      f'--to-destination 192.168.4.1:{config_data["port"]}', filedata)

    with open(accespointsh, 'w') as f:
        f.write(filedata)

    subprocess.run(
        f'sudo chmod a+x {accespointsh}', shell=True)
    subprocess.run(accespointsh, shell=True)


def setup_server_service(config_data):
    print()
    ColorPrint.print(cyan, '▶ Configure server to start at boot')

    serviceConfigPath = './access-point/access-point-server.service'

    with open(serviceConfigPath, 'r') as f:
        filedata = f.read()

    filedata = re.sub(r'WorkingDirectory=.*',
                      f'WorkingDirectory={config_data["working_directory"]}', filedata)
    filedata = re.sub(r'ExecStart=.*',
                      f'ExecStart={config_data["ExecStart"]}', filedata)
    filedata = re.sub(r'Environment=PORT=.*',
                      f'Environment=PORT={config_data["port"]}', filedata)

    with open(serviceConfigPath, 'w') as f:
        f.write(filedata)

    print('We will now register the app as a Linux service and configure')
    print('it to start at boot time.')
    print('The following commands will execute as sudo user.')
    print('Please make sure you look through the file "./access-point/setup-server.sh"')
    print('first before approving.')
    answer = query_yes_no('Continue?', default='yes')

    if not answer:
        return sys.exit(0)

    subprocess.run('sudo chmod a+x ./setup-server.sh',
                   shell=True, cwd='./access-point')
    subprocess.run('./setup-server.sh', shell=True, cwd='./access-point')


def done():
    print()
    ColorPrint.print(cyan, '▶ Done')

    final_msg = (
        'Awesome, we are done here.'
    )
    ColorPrint.print(magenta, final_msg)


def all(config_data):
    print_header()
    check_super_user()
    
    setup_access_point(config_data)

    setup_server_service(config_data)

    done()


if __name__ == "__main__":
    with open("configparameters.json", 'r') as f:
        config_data = json.loads(f.read())
    all(config_data)
