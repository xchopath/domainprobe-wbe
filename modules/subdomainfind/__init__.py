#!/usr/bin/env python3
#
# from subdomainenum import *
# subdomains = SubdomainFind('example.com')

from modules.logging import *
import os
import subprocess

def SubdomainFind(DOMAIN):
	try:
		SUBFINDER_BIN = os.getenv('SUBFINDER_BIN')
		SUBFINDER = subprocess.check_output(['{}'.format(SUBFINDER_BIN), '-d', '{}'.format(DOMAIN), '-recursive', '-silent'])
		SUBDOMAINS = []
		for SUBDOMAIN in SUBFINDER.decode('ascii').split():
			SUBDOMAINS.append(SUBDOMAIN)
		SUBDOMAINS.append(DOMAIN)
		TMP_SUBDOMAINS = SUBDOMAINS
		SUBDOMAINS = []
		[ SUBDOMAINS.append(SUBDOMAIN) for SUBDOMAIN in TMP_SUBDOMAINS if SUBDOMAIN not in SUBDOMAINS ]
		return SUBDOMAINS
	except Exception:
		logger.error(traceback.format_exc())
		return False