#Daniel makarchuk 7858045
#Professor: Sara Rouhani 
#4300
# this file has the fifo forwarding code
import socket
import sys
import select
import json
import time
import random
import pdb


QUE_SIZE = 20
TIME_INTERVAL = 0.1 # send a packet ever 0.1 seconds
lostPackets = [0,0,0,0]# tracks packets of each priority lost, [low,mid,high,ultra]
statPacket = {}# to store the stats packet

class DataStructure:
    def __init__(self):
        self.que = []

    # adds item to back of que if space exists
    def addPacket(self, packet):
        if len(self.que) < QUE_SIZE:# if room, add to que last open spot
            self.que.append(packet)
        else:  # no room in que:
            self.packetLossCounter(packet)
    # adds to the tracking variable lostPackets appropriatly when called      
    def packetLossCounter(self, packet):
        if packet["priority"] == "LOW":
            lostPackets[0] +=1
        elif packet["priority"] == "MID": 
            lostPackets[1] +=1        
        elif packet["priority"] == "HIGH": 
            lostPackets[2] +=1 
        else: # if not anyother priority it must be ULTRA
            lostPackets[3] +=1 
    # remove the first packet in the list  
    def getTop(self):
        toReturn = self.que[0]
        self.removePacket()
        return toReturn    

    def removePacket(self):
        if len(self.que) > 0:
            self.que.pop(0)
    def getSize(self):
        return len(self.que) 
# print dropped stats        
def printLostPackets():
    print("Low dropped: " + str(lostPackets[0]))
    print("Mid dropped: " + str(lostPackets[1]))        
    print("High dropped: " + str(lostPackets[2]))
    print("Ultra dropped: " + str(lostPackets[3]))