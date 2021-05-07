# -*- coding: utf-8 -*-

"""
Parse required settings in order proper API requests to be initiated.

Import this module in the main script inventory_generator.py:
    import modules.frmn_configparser as fc

This module is used to parse the ini configuration file for all required
data for initiating a connection to the Foreman API endpoint, as well as
the arguments provided to the main script which represent the action
which will be taken (using the main script):

    - API request for parsing the Foreman environments - Names and IDs:
        python3 inventory_generator.py --action listenvs

    - API request for parsing the host groups and hosts for each group
        for any given environment ID:
        python3 inventory_generator.py --action parseenv -environment 2

    - Display help message (usage):
        python3 inventory_generator.py [--help | -h]

Fore more detailed information please check the README.md file.
"""

# TODO: implement color prints (colorama module)
# TODO: log errors in logfile (logging module)

__author__ = 'Petyo Kunchev'
__version__ = '2.0.3'
__maintainer__ = 'Petyo Kunchev'
__license__ = 'MIT'

import os
import argparse
from platform import system as sm

import configparser


def print_os_warning():
    """
    Get the operating system family of the host where this program is
    running (Linux, Windows, MacOS).

    Compare with list of supported operating system.

    If the system is not in the supported platforms list, a warning
    message is displayed, stating that the generated inventory file
    must be transferred and used on a system which supports Ansible.
    """
    os_family: str = sm().lower()
    supported_platforms: list = ['linux', 'darwin']

    if os_family not in supported_platforms:
        print(f'Running {os_family.upper()} OS, make sure to transfer the '
              f'generated '
              f'inventory file to a system which supports Ansible.')


def read_settings() -> dict:
    """
    Read the settings from the foreman.ini external configuration file.

    The following parameters with correct values are required to be
    present in the config/foreman.ini file:
    base_url: the Foreman base url
    username: the Foreman user with sufficient privileges
    password: the password for the user
    hfile: the name of the Ansible inventory file which will be created

    :rtype: dict
    :return: settings - parsed data from the supplied 'foreman.ini' file
    """
    config = configparser.ConfigParser()
    confdir: str = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', 'config'))
    foreman_default_ini_path: str = os.path.join(confdir, 'foreman.ini')
    print(f'Reading Foreman configuration from: {foreman_default_ini_path}')
    foreman_ini_path: str = os.environ.get('FOREMAN_INI_PATH',
                                           foreman_default_ini_path)

    config.read(foreman_ini_path)

    settings: dict = {}
    required: list = ['base_url', 'username', 'password', 'hfile']
    missing: list = []

    setting: str
    for setting in required:
        value = config.get('foreman', setting)
        if value is None:
            missing.append(setting)
        settings[setting] = value
    if missing:
        exit('No values, please check your ini configuration file contents!')

    return settings


def parse_args() -> object:
    """
    Parse the script arguments - based on the argparse Python module.

    To list all Foreman environments: '[-a | --action] listenvs'
    To parse a desired Foreman environment: '[-a | --action] parseenv -e
    <envid>

    :rtype: object
    :return: args - the provided script arguments
    """
    # crete parser object
    parser = argparse.ArgumentParser(
        prog='Foreman Ansible Hosts Inventory Parser/Generator',
        description='Parse Foreman API environments and hosts per environment',
        epilog='Enjoy!')

    # add argument for the main action which will be taken
    parser.add_argument('--action', '-a', metavar='<action>',
                        choices=['listenvs', 'parseenv'],
                        action='store', dest="action", default="listenvs",
                        help='[listenvs, parseenv] - the action that will be '
                             'taken. "listenvs" will list all Foreman '
                             'environments with respective IDs. "parseenv" '
                             'will parse the selected/supplied environment ID '
                             'and generate proper Ansible inventory file.')

    # add argument for supplying the desired environment ID for parsing
    parser.add_argument('--environment', '-e', metavar='<environment>',
                        action='store',
                        dest="environment",
                        help='Specifies the Foreman environment ID which '
                             'will be parsed, example: 1, the number matches '
                             'the environment name from the list.')
    
    args = parser.parse_args()

    return args
