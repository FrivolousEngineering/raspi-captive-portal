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


def setup_access_point():
    print()
    ColorPrint.print(cyan, '▶ Setup Access Point (WiFi)')

    print('We will now set up the Raspi as Access Point to connect to via WiFi.')
    print('The following commands will execute as sudo user.')
    print('Please make sure you look through the file "./access-point/setup-access-point.sh"')
    print('first before approving.')
    answer = query_yes_no('Continue?', default='yes')

    if (not answer):
        return sys.exit(0)

    subprocess.run(
        'sudo chmod a+x ./access-point/setup-access-point.sh', shell=True)
    subprocess.run('./access-point/setup-access-point.sh', shell=True)



def setup_server_service():
    print()
    ColorPrint.print(cyan, '▶ Configure server to start at boot')

    # Replace path in file
    serverPath = os.path.join(os.getcwd(), 'server')
    serviceConfigPath = './access-point/access-point-server.service'
    with open(serviceConfigPath, 'r') as f:
        filedata = f.read()
    filedata = re.sub(r'WorkingDirectory=.*',
                      f'WorkingDirectory={serverPath}', filedata)
    with open(serviceConfigPath, 'w') as f:
        f.write(filedata)

    print('We will now register the app as a Linux service and configure')
    print('it to start at boot time.')
    print('The following commands will execute as sudo user.')
    print('Please make sure you look through the file "./access-point/setup-server.sh"')
    print('first before approving.')
    answer = query_yes_no('Continue?', default='yes')

    if (not answer):
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


def all():
    print_header()
    check_super_user()
    
    setup_access_point()

    setup_server_service()

    done()


all()
