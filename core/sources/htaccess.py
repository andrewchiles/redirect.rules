#!/usr/bin/env python3

import os
from core.type import Block
from core.support import REWRITE
from core.base import Base
from typing import List, Set
import re
import requests
from datetime import datetime

# Disable request warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class HTAccess(Base):
    """
    HTAccess class to pull and write @curi0usJack's .htaccess source file
    https://gist.github.com/curi0usJack/971385e8334e189d93a6cb4671238b10
    Current link as of: March 27, 2020

    :param headers:     HTTP headers
    :param timeout:     HTTP timeout
    :param ip_list:     List of seen IPs
    :param agent_list:  List of seen User-Agents
    :param args:        Command line args
    """

    def __init__(self, headers, timeout, args):
        self.headers = headers
        self.timeout = timeout
        self.args = args

        self.return_data = self._process_source()

    def _get_source(self) -> List[str]:
        print("[*]\tPulling @curi0usJack's redirect rules...")

        pwd = os.path.dirname(os.path.realpath(__file__))
        with open(pwd + '/../static/htaccess.txt', 'r') as _file:
            return _file.readlines()

    def _process_source(self) -> Block:
        try:
            # Get the source data
            htaccess_file = self._get_source()
        except:
            return Block()

        print("[*]\tWriting @curi0usJack's redirect rules...")
        # Skip the header comments since we write our own version
        # This means that the line offset is: 12
        htaccess_file = htaccess_file[11:]

        # Line offsets
        START = 12
        STOP = 11  # Slicing

        # Grab the file headers first
        file_headers = htaccess_file[(12-START):(21-STOP)]

        # Data sources as identified in the .htaccess file
        # Use comma delimited strings as keys in case a group has
        # multiple exclusion keywords
        # This data is based on the current raw link, but is subject
        # to changes/updates depending on updated raw links
        file_groups = {
            # Class A Exclusions
            'amazon,aws':      htaccess_file[(32-START):(114-STOP)],
            'forcepoint':      htaccess_file[(115-START):(119-STOP)],
            'domaintools':     htaccess_file[(120-START):(122-STOP)],
            'zscaler':         htaccess_file[(123-START):(126-STOP)],
            'misc':            htaccess_file[(127-START):(137-STOP)],
            'virustotal':      htaccess_file[(138-START):(151-STOP)],
            'trendmicro':      htaccess_file[(152-START):(172-STOP)],
            'bluecoat':        htaccess_file[(173-START):(177-STOP)],
            'urlquery':        htaccess_file[(178-START):(189-STOP)],
            'paloalto':        htaccess_file[(190-START):(207-STOP)],
            'proofpoint':      htaccess_file[(208-START):(224-STOP)],
            'messagelabs':     htaccess_file[(225-START):(249-STOP)],
            'fortigate':       htaccess_file[(250-START):(267-STOP)],
            'symantec':        htaccess_file[(268-START):(306-STOP)],
            'microsoft':       htaccess_file[(307-START):(310-STOP)],
            'microsoft,azure': htaccess_file[(311-START):(435-STOP)],
            'user-agents':     htaccess_file[(437-START):(443-STOP)],
            'barracuda':       htaccess_file[(444-START):(447-STOP)],
            'slackbot':        htaccess_file[(448-START):(451-STOP)],
            'tor':             htaccess_file[(452-START):-1]  # Go until EOF
        }

        ip_list: Set[str] = set()
        agent_list: Set[str] = set()
        # Now let's write each group, but only those the user has not excluded
        for group, content in file_groups.items():
            # Now we need cross reference our exclude list and the keys...
            if all(x not in self.args.exclude for x in group.split(',')):
                for line in content:

                    # Handle one-off rule that points to 'fortinet'
                    if 'http://www.fortinet.com/?' in line:
                        line = re.sub('http://www.fortinet.com/\? +',
                                      '${REDIR_TARGET}\t', line)

                    # Standardize RewriteRule format across the @curi0usjack htaccess rules and our own defined in support.py
                    if 'RewriteRule' in line:
                        line = REWRITE['RULE']

                    # Check if line is a RewriteCond
                    if 'RewriteCond' in line:
                        # Check for IPs to keep a list for de-duping
                        if 'expr' in line:
                            ip_list.add(line.split("'")[1])

                        # Check for User-Agents to keep a list for de-duping
                        if 'HTTP_USER_AGENT' in line:
                            if '"' in line:  # This is specific to one of the user-agents
                                agent_list.add(
                                    re.search('"(.+)"', line).group(1))
                            else:
                                agent_list.add(
                                    re.search('(\^.+\$)', line).group(1))

        return Block(ips=ip_list, agents=agent_list)
