import requests
# find the prime numbers

def prime(p):
    """Print the prime numbers from 2 2 the argument number"""
    for i in range(2, p):
        for n in range(2, i):
            if(i % n ==0):
                print(i, 'equals', n, '*', i//n)
                break
            else:
                print(i, 'can\'t be divided by', n)
        else:
            print(i, 'is a prime number')

prime(100)

print("request start")

# request
url = "https://raw.fastgit.org/freefq/free/master/v2"
headers = {
    'authority':'raw.fastgit.org',
    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language':'en-US,en;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7,zh;q=0.6',
    'cache-control':'max-age=0',
    'if-none-match':'W/"060ff8267dd5732aa8f2f1a19e67ebefd8040bdb0865cf51c06576fc5b8eca88"',
    'sec-ch-ua':'" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    'sec-ch-ua-mobile':'?0',
    'sec-ch-ua-platform':'"Linux"',
    'sec-fetch-dest':'document',
    'sec-fetch-mode':'navigate',
    'sec-fetch-site':'cross-site',
    'sec-fetch-user':'?1',
    'upgrade-insecure-requests':'1',
    'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
}
response = requests.get(url)

print("hell:" + response)

import base64
import json
import os

os.environ

base64.decode()
