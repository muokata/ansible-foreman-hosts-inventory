# -*- coding: utf-8 -*-

"""
Module to parse required settings for initiating proper API requests.

Usage:
- Import this module in the main script: `import modules.frmn_configparser as fc`.

Commands:
    - List Foreman environments: `python3 main.py --action listenvs`
    - Parse host groups/hosts for an environment ID: 
      `python3 main.py --action parseenv --environment 2`
    - Display help: `python3 main.py [--help | -h]`

For detailed information, refer to the README.md file.
"""

import os
import argparse
import configparser
from platform import system as sm

__author__ = 'Petyo Kunchev'
__version__ = '2.0.5'
__maintainer__ = 'Petyo Kunchev'
__license__ = 'MIT'

# TODO: Add color prints (using `colorama`).
# TODO: Log errors to a file and stdout (using `logging`).


def print_os_warning():
    """
    Display a warning if the OS is unsupported for Ansible inventory use.
    """
    os_family = sm().lower()
    supported_platforms = ['linux', 'darwin']

    if os_family not in supported_platforms:
        print(
            f'Warning: Running on {os_family.upper()} OS. Transfer the '
            'generated inventory file to a system that supports Ansible.'
        )


def read_settings() -> dict:
    """
    Parse settings from the `foreman.ini` configuration file.

    Returns:
        dict: Configuration parameters (base_url, username, password, hfile).
    """
    config = configparser.ConfigParser()
    confdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config'))
    default_ini_path = os.path.join(confdir, 'foreman.ini')
    print(f'Reading Foreman configuration from: {default_ini_path}')

    foreman_ini_path = os.environ.get('FOREMAN_INI_PATH', default_ini_path)
    config.read(foreman_ini_path)

    required = ['base_url', 'username', 'password', 'hfile']
    settings = {}
    missing = []

    for key in required:
        value = config.get('foreman', key, fallback=None)
        if not value:
            missing.append(key)
        settings[key] = value

    if missing:
        raise ValueError(
            f'Missing required configuration keys in `foreman.ini`: {", ".join(missing)}'
        )

    return settings


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments (action, environment).
    """
    parser = argparse.ArgumentParser(
        prog='Foreman Ansible Hosts Inventory Parser/Generator',
        description='Parse Foreman API environments and hosts per environment',
        epilog='Enjoy!'
    )

    parser.add_argument(
        '-a', '--action',
        metavar='<action>',
        choices=['listenvs', 'parseenv'],
        default='listenvs',
        help='Specify the action: "listenvs" lists all Foreman environments. '
             '"parseenv" parses the supplied environment ID and generates an '
             'Ansible inventory file.'
    )

    parser.add_argument(
        '-e', '--environment',
        metavar='<environment>',
        help='Provide the Foreman environment ID to parse. Example: 1.'
    )

    return parser.parse_args()
