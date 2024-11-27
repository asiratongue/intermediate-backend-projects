import argparse
import asyncio
import django 
import subprocess
from django.core.management import call_command
import os 
import atexit 

#python broadcast-server.py -s
#python broadcast-server.py -c -a CONGLOMERATE


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Broadcast_Server.settings')
django.setup()

parser = argparse.ArgumentParser(description="Broadcast Server", usage="a CLI for broadcasting messages.")
parser.add_argument('-s', '--start', action='store_true', help="start the server")
parser.add_argument('-c', '--connect', action='store_true', help="launch a client")
parser.add_argument('-a', '--authorise', type= str, help='enter your psk here')

args = parser.parse_args()
start = args.start
connect = args.connect
auth = args.authorise


redis_result = subprocess.Popen(['docker', 'run', '--rm', '-p', '6379:6379', 'redis:7'], text=True)

      

async def serverstart():

    server_process = subprocess.run(['python', 'manage.py', 'runserver'])


async def clientstart():

    print("Starting wscat subprocess...")
    print(f"{auth}")
    client_process = subprocess.run(["cmd", "/c", "start", "cmd", "/K", f"wscat -c ws://127.0.0.1:8000/ws/endpoint/?psk={auth}"], capture_output=True, shell=True)

def terminate_redis():
    print("Terminating Redis . . . ")
    redis_result.terminate()
    redis_result.wait()


if start == True:
    asyncio.run(serverstart())

else:
    pass

if connect == True:
    asyncio.run(clientstart())

else:
    pass

atexit.register(terminate_redis)


#add main.py to system variables PATH . . .

