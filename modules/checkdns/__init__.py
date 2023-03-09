#!/usr/bin/env python3
#
# from checkdns import *
# dns_check = CheckDNS('example.com')

from modules.logging import *
import subprocess
import json
import os

def CheckDNS(DOMAIN):
	try:
		DNSX_BIN = os.getenv('DNSX_BIN')
		domain = subprocess.Popen(["echo", "{DOMAIN}".format(DOMAIN=DOMAIN)], stdout=subprocess.PIPE)
		get_dns = subprocess.run(['{}'.format(DNSX_BIN), '-a', '-aaaa', '-cname', '--resp', '-retry', '3', '-json', '-silent'], stdin=domain.stdout, capture_output=True, text=True)
		data = json.loads(get_dns.stdout)
		timestamp = data['timestamp']
		del data['timestamp']
		del data['resolver']
		del data['all']
		if data == None:
			return None
		return data
	except Exception:
		logger.error(traceback.format_exc())
		return None