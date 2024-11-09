import argparse
from flask import Flask, jsonify
from cachetools import LRUCache
import requests
#python main.py -p 2000 -o https://dummyjson.com/ 
#curl -X GET http://127.0.0.1:2000/recipes
#i implemented the clearcache function as a flask endpoint instead of as a CLI command.

parser = argparse.ArgumentParser(description="use this as a proxy caching server", usage="a CLI used as a Caching proxy server")

parser.add_argument('-p', '--port', type=int, required=True, help="enter your port number here")
parser.add_argument('-o','--origin', type=str, help="enter your site to proxy to here")
parser.add_argument('-c','--clearcache', action='store_true')

args = parser.parse_args()
port = args.port
origin = args.origin
cache = LRUCache(maxsize=3)

app = Flask(__name__)

def get_data(key, url):
    
    if args.clearcache:
        cache.clear()
    else:

        msg = {'X-cache':'HIT'}
        if key in cache:
            print(cache)
            return cache[key], msg 
        
        else:
            msg = {'X-cache':'MISS'}
            res = requests.get(url)
            cache[key] = res 
            return res, msg 

@app.route('/<string:link>', methods = ['GET'])
def proxyrequest(link):

    url = origin + link
    print(url[-6:-1]) 

    data, message = get_data(url[-6:-1], url)
    rawdata = data.json()
    combined_data = {"data" : rawdata,
                     "message": message
                     }

    return jsonify(combined_data)

@app.route('/clearcache', methods = ['GET'])
def cacherequest():
    cache.clear()
    return jsonify({"message" : "cache cleared"})



if __name__ == '__main__':
    app.run(port=port)  

     