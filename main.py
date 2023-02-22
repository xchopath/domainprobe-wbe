#!/usr/bin/env python3

from modules.logging import *
from modules.subdomainfind import *
from modules.checkhttp import *
from modules.checkdns import *
from flask import Flask, request, jsonify
from pymongo import MongoClient, UpdateOne
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import redis
import threading
import time
import datetime
import pytz
import requests
import json
import gzip

LISTEN_ADDR = os.getenv('LISTEN_ADDR')
LISTEN_PORT = int(os.getenv('LISTEN_PORT'))
APP_DEBUG = eval(os.getenv('APP_DEBUG'))
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_NAME = os.getenv('MONGODB_NAME')
REDIS_URI = os.getenv('REDIS_URI')

redis_connect = redis.Redis.from_url(REDIS_URI)
mongo_client = MongoClient(MONGODB_URI)
mongodb = mongo_client[MONGODB_NAME]

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

def GetFullResponse(url):
	def HeaderBodyMerger(headers, body):
		try:
			full_response = []
			for header in headers:
				full_response.append(str(header) + ': ' + str(headers[header]))
			full_response = '\n'.join([stings for stings in full_response])
			full_response = full_response + '\n\n' + body 
			return '{}'.format(str(full_response))
		except:
			return None
	try:
		req = requests.get('{}'.format(url), allow_redirects=True, verify=False, timeout=10)
		merge_response = []
		for redirect_response in req.history:
			get_redirect_response = HeaderBodyMerger(redirect_response.headers, redirect_response.text)
			merge_response.append(get_redirect_response)
		merge_response.append(HeaderBodyMerger(req.headers, req.text))
		merged_response = ''.join([stings for stings in merge_response])
		return '{}'.format(str(merged_response))
	except:
		return None

def datetimenow():
	TZ = pytz.timezone('Asia/Jakarta')
	datetimenow = datetime.datetime.now()
	datetimenow = datetimenow.replace(tzinfo=TZ, microsecond=0).isoformat()
	return datetimenow

def CheckHTTPFull(host):
	try:
		http = CheckHTTP(host)
		http_response = GetFullResponse(http['url'])
		return {'info': http, 'response': http_response}
	except Exception:
		logger.error(traceback.format_exc())
		return None

def DomainProbe(host):
	try:
		dns = CheckDNS(host)
		http = CheckHTTPFull(host)
		result = {'dns': dns, 'http': http}
		return result
	except Exception:
		logger.error(traceback.format_exc())
		return None

def strdecompress(string):
	decompressed_data = gzip.decompress(string)
	decompressed_string = str(decompressed_data, 'utf-8')
	return decompressed_string

def strcompress(string):
	compressed_data = gzip.compress(bytes(string, 'utf-8'))
	return compressed_data

def RedisCacheClear():
	logger.info('RedisCacheClear daemon run!')
	while True:
		keynames = ['domprobcache', 'subdomains']
		for keyname in keynames:
			keylist = [ str(row, 'utf-8') for row in redis_connect.hgetall(keyname + ':time') ]
			for key in keylist:
				current_time = int(time.time())
				last_update = int(redis_connect.hget(keyname + ':time', key))
				ago = current_time - last_update
				if ago > 86400:
					redis_connect.hdel(keyname + ':time', key)
					logger.info('{} has deleted from cache'.format(str(key)))
		time.sleep(60)

@app.route('/api/domainprobe/subdomain/<host>', methods=['GET'])
def domainprobesubdomain(host):
	try:
		keyname = 'subdomains'
		get_redis = redis_connect.hget(keyname + ':time', host)
		if not get_redis == None:
			data = mongodb['subdomain'].find({'main': host}, {'main': False, 'updated_on': False})
			data = [ row['_id'] for row in data ]
			return jsonify(list(data)), 200
		subdomains = SubdomainFind(host)
		current_time = int(time.time())
		data_upserts = [ {'_id': hit, 'main': host, 'updated_on': datetimenow()} for hit in subdomains ]
		upserts = [ UpdateOne({'_id': row['_id']}, {'$setOnInsert': row}, upsert=True) for row in data_upserts ]
		mongodb['subdomain'].bulk_write(upserts)
		redis_connect.hset(keyname + ':time', host, current_time)
		return jsonify(subdomains), 200
	except Exception:
		logger.error(traceback.format_exc())
		return {'error': 500, 'message': 'unknown error'}, 500

@app.route('/api/domainprobe/probe/<host>', methods=['GET'])
def domainprobescan(host):
	try:
		keyname = 'domprobcache'
		get_redis = redis_connect.hget(keyname + ':time', host)
		if not get_redis == None:
			data = mongodb['domainprobe'].find_one({"_id": host})
			return jsonify(data), 200
		domainprobe = DomainProbe(host)
		current_time = int(time.time())
		data = {'_id': host, 'data': domainprobe, 'updated_on': datetimenow()}
		redis_connect.hset(keyname + ':time', host, current_time)
		mongodb['domainprobe'].update_one({"_id": host}, {"$set": data}, upsert=True)
		return jsonify(domainprobe), 200
	except Exception:
		logger.error(traceback.format_exc())
		return {'error': 500, 'message': 'unknown error'}, 500

@app.route('/api/domainprobe/domains', methods=['GET'])
def domainprobedomains():
	try:
		data = mongodb['subdomain'].find({}, {'_id': True, 'updated_on': False, 'data': False})
		data = [ row['_id'] for row in data ]
		return jsonify(list(data)), 200
	except Exception:
		logger.error(traceback.format_exc())

if __name__ == '__main__':
	requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
	thread = threading.Thread(name='Redis Clear Cache', target=RedisCacheClear).start()
	app.run(host=LISTEN_ADDR, port=LISTEN_PORT, debug=APP_DEBUG)