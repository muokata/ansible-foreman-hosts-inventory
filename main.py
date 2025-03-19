#!/usr/bin/env python3

import modules.frmn_envparser as fe
import modules.frmn_confparser as fc


def generate_ansible_hosts():
    """
    Parse the Foreman API to list all environments and generate an Ansible inventory 
    hosts file with groups containing hosts for the desired environment. 
    The environment ID must be provided as an argument when running the script.

    This function utilizes methods from the imported modules based on the script's 
    input parameters. The resulting output is saved locally in the file specified 
    in the configuration.
    """
    # Load settings and parse command-line arguments
    settings = fc.read_settings()
    arguments = fc.parse_args()
    env_id = str(arguments.environment)

    # Initialize the AnsibleInventory with required parameters
    hosts = fe.AnsibleInventory(
        env_id,
        settings['base_url'],
        settings['username'],
        settings['password'],
        settings['hfile']
    )

    if arguments.action == 'listenvs':
        # List all environments
        hosts.parse_envs()
    elif arguments.action == 'parseenv':
        # Parse environment hosts
        if arguments.environment is not None:
            fc.print_os_warning()
            hosts.parse_hosts(env_id)
        else:
            exit(
                "Error: Please provide a valid Foreman environment ID. "
                "You can list all environments using the <-a listenvs | --action listenvs> option, "
                "or access help using <-h | --help>."
            )


def main():
    """
    The main entry point of the script, which triggers the generation 
    of Ansible hosts.
    """
    generate_ansible_hosts()


if __name__ == '__main__':
    main()
