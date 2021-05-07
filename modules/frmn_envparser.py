# -*- coding: utf-8 -*-

"""
Initiate API calls to the Foreman API endpoint(s) and parse the
environments and the hosts groups with hosts for desired environment.

Import in this module in the main script frmn_envparser.py:
    import modules.frmn_envparser as fe

Fore more detailed information check the README.md file.
"""

# TODO: implement color prints (colorama module)
# TODO: log errors instead of printing (logging module)

__author__ = 'Petyo Kunchev'
__version__ = '2.0.1'
__maintainer__ = 'Petyo Kunchev'
__license__ = 'MIT'

import os
from pathlib import Path
from typing import Any
from datetime import datetime

import json
import urllib3
import requests
from requests.models import Response
from collections import defaultdict

# suppress warnings for self-signed SSL Foreman certificates (if used)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AnsibleInventory(object):
    """
    AnsibleInventory hosts file generation class.

    This class is used to represent generation of Ansible inventory
    hosts file by using Foreman API requests. The hosts written to
    the inventory file must already be members of any Foreman host group
    and environment.

    Methods
    -------
    parse_envs()
        Parse the Foreman API and print the environments configured
    parse_hosts(environment_id: str = None)
        Parse the Foreman API per env and generate Ansible hosts file
    """

    def __init__(self, envid, base_url, username, password, hostfile):
        """
        Inits the AnsibleInventory class.

        Args:
            envid: The Foreman environment ID parsed from args
            base_url: The base Foreman API URL
            username: The API username
            password: The password for the API user
            hostfile: The output inventory file which will be created
        """
        self.base_url: str = base_url
        self.username: str = username
        self.password: str = password
        self.envid: str = envid
        self.hfile: str = str(Path.home()) + os.path.sep + hostfile + envid

    def parse_envs(self):
        """
        Parse the Foreman API, collect and print to the console data for
        the available and configured environments: env name and env ID.
        """
        # API parse related - Foreman environments, timeout is set to 5
        try:
            r: Response = requests.get(self.base_url, verify=False, timeout=5,
                                       auth=(self.username, self.password))
            r.raise_for_status()
            print(f'API request status code: {r.status_code}')
            response: str = r.text
            env_data: dict = json.loads(response)
            data: dict = env_data['results']  # get data from the results key
            parsed_envs: list = []  # define list to append env names to
            parsed_env_ids: list = []  # define list to append env IDs to
            results_dict: defaultdict[Any, list] = defaultdict(list)

            # append env names and env IDs to their respective lists
            for data in data:
                env_name: object = data['name']  # filter environment name
                env_id: object = data['id']  # get environment ID
                parsed_envs.append(env_name)
                parsed_env_ids.append(env_id)

            # zip the two lists into single defaultdict
            for ename, eid in zip(parsed_envs, parsed_env_ids):
                results_dict[ename].append(eid)

            # print the results for the selected environment
            print('-All Foreman environments and their respective IDs-')
            [print(f'{n:<15} {i}') for n, i in results_dict.items()]

        # catch possible requests exceptions
        except requests.exceptions.HTTPError as errh:
            print(f'HTTP error: {errh}')
        except requests.exceptions.ConnectionError as errc:
            print(f'Connection error: {errc}')
        except requests.exceptions.Timeout as errt:
            print(f'Timeout error: {errt}')
        except requests.exceptions.RequestException as errr:
            print(f'General error: {errr}')

    def parse_hosts(self, environment_id: str = None):
        """
        Parse the Foreman API per provided environment and generate the
        Ansible inventory hosts file. The file is saved locally in the
        current user's home folder.

        When ran against a specific foreman environment ID, this script
        generates Ansible hosts file, based on the obtained from Foreman
        data, containing host groups and adjacent hosts.

        Parameters
        ----------
        environment_id (str): Foreman environment ID provided as arg
        """
        # construct the Foreman API URL for the selected environment -
        # results are limited up to 100000, change accordingly
        url: str = f'{self.base_url + environment_id}/hosts?per_page=100000'
        print('Starting hosts file generation, please wait...')

        # generate time stamp for the hosts file header comments
        now: datetime = datetime.now()
        fdate: str = now.strftime('%d/%m/%Y %H:%M:%S')

        print(f'Parsing Foreman environment with id: [{environment_id}]')

        # API parse related - Foreman hosts, timeout is set to 5
        try:
            r: Response = requests.get(url, verify=False, timeout=5,
                                       auth=(self.username, self.password))
            r.raise_for_status()
            print(f'API request status code: {r.status_code}')
            response: str = r.text
            foreman_data: dict = json.loads(response)
            data = foreman_data['results']  # get data from the results key
            parsed_groups: list = []  # define list to append groups to
            parsed_hosts: list = []  # define list to append hosts to
            results_dict: defaultdict[Any, list] = defaultdict(list)

            # append groups and hosts to their respective lists
            for data in data:
                host_group: object = data['hostgroup_title']  # host groups
                name: object = data['name']  # servers in each host group
                parsed_groups.append(host_group)
                parsed_hosts.append(name)

            # zip the two lists into single defaultdict
            for group, host in zip(parsed_groups, parsed_hosts):
                results_dict[group].append(host)

            # write the results to the desired Ansible inventory file
            try:
                with open(self.hfile, 'w') as hosts:
                    hosts.write(f'# Ansible hosts file for Foreman inventory '
                                f'id {environment_id} generated on {fdate}\n')
                    for key in results_dict:
                        hosts.write(f'\n[{key}]\n')
                        for val in results_dict[key]:
                            hosts.write(f'{val}\n')
                print(f'The following inventory file has been generated '
                      f'locally: {self.hfile}')
            except IOError:
                print(f'Error opening the target file: {self.hfile}, please '
                      f'check.')

                # catch possible requests exceptions
        except requests.exceptions.HTTPError as errh:
            print(f'HTTP error: {errh}')
        except requests.exceptions.ConnectionError as errc:
            print(f'Connection error: {errc}')
        except requests.exceptions.Timeout as errt:
            print(f'Timeout error: {errt}')
        except requests.exceptions.RequestException as errr:
            print(f'General error: {errr}')
