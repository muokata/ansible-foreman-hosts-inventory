#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import the local custom modules required
import modules.frmn_envparser as fe
import modules.frmn_confparser as fc


def generate_ansible_hosts():
    """
    Parse the Foreman API: list all environments, generate Ansible
    inventory hosts file with groups containing hosts for the desired
    environment. The environment id is provided as a script argument.

    Call the appropriate methods from the imported modules, based on the
    input parameters provided to the script.

    Output is stored locally in file, specified in the configuration.
    """
    settings = fc.read_settings()
    arguments = fc.parse_args()
    envid = str(arguments.environment)  # get the parsed env id as str
    hosts = fe.AnsibleInventory(envid,
                                settings['base_url'],
                                settings['username'],
                                settings['password'],
                                settings['hfile'])

    # if action is 'listenvs', call fp.parse_envs() method
    if arguments.action == 'listenvs':
        hosts.parse_envs()

    # if action is 'parseenv', call fp.parse_hosts(arg) method
    if arguments.action == 'parseenv':
        if arguments.environment is not None:
            fc.print_os_warning()
            hosts.parse_hosts(envid)
        else:
            exit('Please provide (correct) Foreman environment ID. List all '
                 'environments supplying the <-a listenvs | --action '
                 'listenvs> argument to the script, or display full help '
                 'message <-h | --help>')


def main():
    generate_ansible_hosts()


if __name__ == '__main__':
    main()
