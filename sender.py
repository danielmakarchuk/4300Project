#Daniel makarchuk 7858045
#Professor: Sara Rouhani 
#4300
#this file contains the portion creating packets and sending them to the router
import socket
import sys
import select
import json
import time
import random
import pdb
import uuid


PACKETS_NUM = 500 # number of packets to send
PRIORITY_LOW_CHANCE = 0.45 # chance a packet to send is ultra priority
PRIORITY_MID_CHANCE = 0.25 # chance a packet to send is ultra priority
PRIORITY_HIGH_CHANCE = 0.2 # chance a packet to send is ultra priority
PRIORITY_ULTRA_CHANCE = 0.1 # chance a packet to send is ultra priority
TIME_INTERVAL = 0.05 # send a packet ever 0.05 seconds

priSent = [0,0,0,0]#tracks packets of each priority sent, [low,mid,high,ultra]
statPack = {"priority": "STAT", 
            "startTime": time.time(), 
            "endTime": time.time(), 
            "lowSent": 0, 
            "midSent": 0,
            "highSent": 0,
            "ultraSent": 0
            }#stats packet
# builds a "packet" to send that has a priority and a creation time.
def packetBuilder():
    toReturn = {"priority": packetPriority(), "startTime": time.time(), "endTime": None}
    return toReturn
# return a priority for the packet.
# the priority is randomly chosen
def packetPriority():
    toReturn = "LOW" 
    r = random.random()
    if r >= PRIORITY_LOW_CHANCE and r <= (PRIORITY_LOW_CHANCE + PRIORITY_MID_CHANCE):
       toReturn = "MID"
       priSent[1] += 1
    elif r >= (PRIORITY_LOW_CHANCE + PRIORITY_MID_CHANCE) and r <= (PRIORITY_LOW_CHANCE + PRIORITY_MID_CHANCE + PRIORITY_HIGH_CHANCE):
       toReturn = "HIGH"
       priSent[2] += 1
    elif r >= (PRIORITY_LOW_CHANCE + PRIORITY_MID_CHANCE + PRIORITY_HIGH_CHANCE):
       toReturn = "ULTRA"
       priSent[3] += 1
    else:
        priSent[0] += 1
    return toReturn
# send time to reciever to ensure times are semi synced
hostnameRec = socket.gethostname()# use local hostname as host
portRec = 8001



timesyncsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:# try to send time.time() to reciever to be able to calculate the clock differences
    timesyncsoc.connect((hostnameRec, portRec))
    timeStuff = {"priority": "TIME", "time": time.time()}
    timesyncsoc.sendall((json.dumps(timeStuff)).encode())
except Exception as e:
    print("Something happened when sending time.  program stopped")
    print(e)
    sys.exit(0)
hostname = socket.gethostname()# use local hostname as host
port = 8000    
sendersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:# try to connect to router
    sendersocket.connect((hostname, port))
except Exception as e:
    print("Something happened when connecting")
    print(e)

# attempt to send a packet
def doSend(packet):
    try:
        sending = (json.dumps(packet)).encode()
        sendersocket.sendall(sending)
    except Exception as e:
        
        print("Something happened when sending, stopping program")
        print(e)   
        sys.exit(0)

# send the packets        
for each in range(PACKETS_NUM):
    toSend = packetBuilder()
    doSend(toSend)
    time.sleep(TIME_INTERVAL) # stall program for time interval
statPack["lowSent"] = priSent[0]
statPack["midSent"] = priSent[1]
statPack["highSent"] = priSent[2]
statPack["ultraSent"] = priSent[3]
statPack["endTime"] = time.time()# add ending time    
doSend(statPack)# send stats to router

print("Sender finished!")