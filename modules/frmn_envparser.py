# -*- coding: utf-8 -*-

"""
Initiate API calls to the Foreman API endpoint(s) and parse the environments and the host groups 
with hosts for the desired environment.

Import in this module in the main script frmn_envparser.py: import modules.frmn_envparser as fe
For more detailed information check the README.md file.
"""

# TODO: implement color prints (use 'colorama')
# TODO: log errors to logfile alongside with printing to stdout (use 'logging')

__author__ = "Petyo Kunchev"
__version__ = "2.0.4"
__maintainer__ = "Petyo Kunchev"
__license__ = "MIT"

import os
from pathlib import Path
from typing import Any
from datetime import datetime
import json
import urllib3
import requests
from requests.models import Response
from collections import defaultdict

# Suppress warnings for self-signed SSL Foreman certificates (if used)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AnsibleInventory:
    """
    AnsibleInventory hosts file generation class.

    This class is used to represent generation of Ansible inventory hosts file by using Foreman API requests. The
    hosts written to the inventory file must already be members of any Foreman host group and environment.

    Methods:
        parse_envs() - Parse the Foreman API and print the environments configured
        parse_hosts(environment_id: str = None) - Parse the Foreman API per env and generate Ansible hosts file
    """

    def __init__(self, envid, base_url, username, password, hostfile):
        """
        Initializes the AnsibleInventory class.

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
        try:
            response: Response = requests.get(
                self.base_url, verify=False, timeout=5, auth=(self.username, self.password)
            )
            response.raise_for_status()
            print(f"API request status code: {response.status_code}")
            env_data: dict = response.json()
            data: dict = env_data["results"]
            parsed_envs, parsed_env_ids = [], []
            results_dict: defaultdict[Any, list] = defaultdict(list)

            for datum in data:
                parsed_envs.append(datum["name"])
                parsed_env_ids.append(datum["id"])

            for env_name, env_id in zip(parsed_envs, parsed_env_ids):
                results_dict[env_name].append(env_id)

            print("-All Foreman environments and their respective IDs-")
            [print(f"{name:<15} {ids}") for name, ids in results_dict.items()]

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"General error: {req_err}")

    def parse_hosts(self, environment_id: str = None):
        """
        Parse the Foreman API per provided environment and generate the Ansible inventory hosts file. The file is
        saved locally in the current user's home folder.

        Parameters:
            environment_id (str): Foreman environment ID provided as arg
        """
        url: str = f"{self.base_url}{environment_id}/hosts?per_page=100000"
        print("Starting hosts file generation, please wait...")

        now: datetime = datetime.now()
        timestamp: str = now.strftime("%d/%m/%Y %H:%M:%S")

        print(f"Parsing Foreman environment with id: [{environment_id}]")

        try:
            response: Response = requests.get(
                url, verify=False, timeout=5, auth=(self.username, self.password)
            )
            response.raise_for_status()
            print(f"API request status code: {response.status_code}")
            foreman_data: dict = response.json()
            data = foreman_data["results"]
            parsed_groups, parsed_hosts = [], []
            results_dict: defaultdict[Any, list] = defaultdict(list)

            for datum in data:
                parsed_groups.append(datum["hostgroup_title"])
                parsed_hosts.append(datum["name"])

            for group, host in zip(parsed_groups, parsed_hosts):
                results_dict[group].append(host)

            try:
                with open(self.hfile, "w") as hosts:
                    hosts.write(
                        f"# Ansible hosts file for Foreman inventory id {environment_id} "
                        f"generated on {timestamp}\n"
                    )
                    for key, values in results_dict.items():
                        hosts.write(f"\n[{key}]\n")
                        for value in values:
                            hosts.write(f"{value}\n")
                print(f"The following inventory file has been generated locally: {self.hfile}")
            except IOError:
                print(f"Error opening the target file: {self.hfile}, please check.")

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"General error: {req_err}")
