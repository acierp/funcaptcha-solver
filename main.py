import speech_recognition as sr
import requests
import termcolor
import random
import string 
import time
import os
import threading
from itertools import cycle

os.system('color')

with open('proxies.txt','r+', encoding='utf-8') as f:
	ProxyPool = cycle(f.read().splitlines())


def get_token():
	r = requests.post('https://client-api.arkoselabs.com/fc/gt2/public_key/476068BF-9607-4799-B53D-966BE98E2B81', proxies=proxy, data={
		'bda': '',
		'public_key': '476068BF-9607-4799-B53D-966BE98E2B81',
		'site': 'https://www.roblox.com',
		'userbrowser': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
		'rnd': f'0.{random.choice("12334565789")}'
	})
	return r.json()['token']

def captchacsrf():
    req = requests.Session()
    xsrf = req.post("https://auth.roblox.com/v1/login",headers={"X-CSRF-TOKEN":""}).headers['x-csrf-token']
    return xsrf

def recognize(audiofilename):
	r = sr.Recognizer()
	with sr.AudioFile(audiofilename + '.wav') as s:
		data = r.record(s)
		raw = r.recognize_google(data)
		answer = ''
		for char in raw:
			if char.isdigit():
				answer += char
		return answer

def getDirectory(name):   
	mypath = os.getcwd()
	path = rf"{mypath}\Audios\{name}"
	return path

def solveCaptcha(token, proxy, threadnum):
	session_token = token.split('|')[0]
	print(f'[{threadnum}]: Attempting to solve {session_token}')
	r = requests.get(f'https://client-api.arkoselabs.com/fc/get_audio/?session_token={session_token}&analytics_tier=40&r=us-east-1&game=1&language=en', proxies=proxy)
	res = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 7)) 
	dirpath = getDirectory(res)
	open(dirpath + '.wav', 'wb+').write(r.content)
	
	
	r = requests.post('https://client-api.arkoselabs.com/fc/audio/',
		
		headers = {
			'authority': 'client-api.arkoselabs.com',
			'accept': '*/*',
			'cache-control': 'no-cache',
			'x-newrelic-timestamp': str(round(time.time())),
			'x-requested-with': 'XMLHttpRequest',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
			'content-type': 'application/x-www-form-urlencoded',
			'origin': 'https://client-api.arkoselabs.com',
			'sec-fetch-site': 'same-origin',
			'sec-fetch-mode': 'cors',
			'sec-fetch-dest': 'empty',
			'accept-language': 'en-US,en;q=0.9'
		},
		data={
			'session_token': session_token,
			'language': 'en',
			'r': 'us-east-1',
			'audio_type': '2',
			'response': recognize(dirpath),
			'analytics_tier': '40'
		},
		proxies=proxy
		)
	try:
		if r.json()['response'] == 'correct':
			print(termcolor.colored(f'[{threadnum}]: Successfully solved captcha!', color='green'))
			print(r.text)
		elif r.json()['response'] != 'correct':
			print(f'[{threadnum}]: ratelimited on funcaptcha API or response was incorrect. Retrying.')
			proxy = {"https": "https://" + next(ProxyPool)}
		else:
			print(f'[{threadnum}]: Captcha solver response incorrect.')
	except KeyError:
		pass
	except:
		pass

def worker(proxy, threadnum):
	while True:
		token = get_token()
		solveCaptcha(token, proxy, threadnum)

for threadnum in range(50):
	proxy = {"https": "https://" + next(ProxyPool)}
	threading.Thread(target=worker, args=[proxy, threadnum]).start()