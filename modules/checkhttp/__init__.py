#!/usr/bin/env python3
#
# from checkhttp import *
# httpcheck = CheckHTTP('example.com')

from modules.logging import *
import subprocess
import json
import os

def CheckHTTP(DOMAIN):
	try:
		HTTPX_BIN = os.getenv('HTTPX_BIN')
		target = subprocess.Popen(["echo", "{DOMAIN}".format(DOMAIN=DOMAIN)], stdout=subprocess.PIPE)
		get_http_list = subprocess.run(['{}'.format(HTTPX_BIN), '-timeout', '5', '-retries', '3', '-status-code', '-tech-detect', '-json', '-silent'], stdin=target.stdout, capture_output=True, text=True)
		result = []
		for http_list in get_http_list.stdout.split('\n'):
			if 'url' in http_list:
				data = json.loads(http_list)
				try:
					tech = data['tech']
				except Exception:
					tech = None
					pass
				try:
					content_type = data['content_type']
				except:
					content_type = None
					pass
				data_parsed = {'url': data['url'], 'status_code': data['status_code'], 'host': data['host'], 'port': data['port'], 'content_type': content_type, 'technologies': tech}
				result.append(data_parsed)
		if result == []:
			return False
		return result[0]
	except Exception:
		logger.error(traceback.format_exc())
		return False