#!/usr/bin/env python3
# usage: put the list of domains and the cpt given by get_sites_using_plugin.sh
# python activate_plugin.py

import subprocess

domains = [
]

nb_domains = 0

assert (len(domains) == nb_domains)


for domain in domains:
    subprocess.check_call(['wp_sites', 'plugin', 'deactivate', 'lemon-way-for-ecommerce', '--url=' + domain])
    subprocess.check_call(['wp_sites', 'plugin', 'activate', 'lemon-way-for-ecommerce', '--url=' + domain])
