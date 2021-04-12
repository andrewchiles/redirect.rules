#!/usr/bin/env python3

from core.type import Block
from core.sources.utils import fix_ip
from core.base import Base
from core.support import REWRITE
import re
import requests
from datetime import datetime

# Disable request warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Import static data

# Import parent class


class Azure(Base):
    """
    # Add Microsoft Azure IPs: https://www.microsoft.com/en-us/download/confirmation.aspx?id=41653

    :param headers:     HTTP headers
    :param timeout:     HTTP timeout
    """

    def __init__(self, headers, timeout):
        self.headers = headers
        self.timeout = timeout

        self.return_data = self._process_source()

    def _get_source(self):
        print("[*]\tPulling Microsoft Azure IP/network list...")

        # Go to download page
        ms_download_page = requests.get(
            'https://www.microsoft.com/en-us/download/confirmation.aspx?id=41653',
            headers=self.headers,
            timeout=self.timeout,
            verify=False
        ).content.decode('utf-8').split('\n')

        # Grab download link
        for line in ms_download_page:
            if 'click here' in line:
                link = re.search('href="(.+?)"', line.strip()).group(1)

        # Download IP list
        azure_subnets = requests.get(
            link,
            headers=self.headers,
            timeout=self.timeout,
            verify=False
        )

        # Decode from a bytes object and split into a list of lines
        return azure_subnets.content.decode('utf-8').split('\n')

    def _process_source(self):
        try:
            # Get the source data
            azure_subnets = self._get_source()
        except:
            return Block()

        def get_ip(html):
            return re.search('"(.+?)"', html.strip()).group(1)

        subnets = (s for s in azure_subnets if 'IpRange Subnet' in s)
        new_ips_raw = (get_ip(h) for h in subnets)
        new_ips = {fix_ip(ip) for ip in new_ips_raw if ip != ''}
        return Block(ips=new_ips)


class Office365(Base):
    """
    Add Microsoft Office365 IPs: https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7
    https://rhinosecuritylabs.com/social-engineering/bypassing-email-security-url-scanning/

    :param headers:     HTTP headers
    :param timeout:     HTTP timeout
    """

    def __init__(self, headers, timeout):
        raise Exception('Not supported')
        self.headers = headers
        self.timeout = timeout

        self.return_data = self._process_source()

    def _get_source(self):
        print("[*]\tPulling Microsoft Office 365 IP/Host list...")

        o365_networks = requests.get(
            'https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919976789a7',
            headers=self.headers,
            timeout=self.timeout,
            verify=False
        )

        # Return JSON object
        return o365_networks.json()

    def _process_source(self) -> Block:
        try:
            # Get the source data
            o365_networks = self._get_source()
        except:
            return Block()

        # Since this returns a JSON object with both URLs and IPs,
        # lets handle accordingly
        # This is going to be messy since we are going to attempt to
        # note each service
        o365_ips = []
        o365_urls = []

        # Loop over the JSON objects
        # This is gross...
        for network in o365_networks:
            # Make sure we have IPs/URLs to handle
            if any(x in network.keys() for x in ['ips', 'urls']):
                # self.workingfile.write("\t# %s\n" % network['serviceAreaDisplayName'])
                # If we have URLs, lets document them
                if 'urls' in network.keys():
                    for url in network['urls']:

                        # Fix wildcard URL's to work with regex
                        if url.startswith('*'):
                            url = '.' + url

                        url = '^%s$' % url  # Add regex style to host

                        if url not in self.host_list and url != '':
                            # self.workingfile.write(REWRITE['COND_HOST'].format(HOSTNAME=url))
                            self.host_list.append(url)

                # If we have IPs, lets document them
                if 'ips' in network.keys():
                    for ip in network['ips']:
                        if ':' not in ip:  # Ignore v6
                            # Convert /31 and /32 CIDRs to single IP
                            ip = re.sub('/3[12]', '', ip)

                            # Convert lower-bound CIDRs into /24 by default
                            # This is assmuming that if a portion of the net
                            # was seen, we want to avoid the full netblock
                            ip = re.sub(
                                '\.[0-9]{1,3}/(2[456789]|30)', '.0/24', ip)

                            # Check if the current IP/CIDR has been seen
                            if ip not in self.ip_list and ip != '':
                                # self.workingfile.write(REWRITE['COND_IP'].format(IP=ip))
                                # Keep track of all things added
                                self.ip_list.append(ip)

        return Block()
