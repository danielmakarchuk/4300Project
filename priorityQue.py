#Daniel makarchuk 7858045
#Professor: Sara Rouhani 
#4300
# this file contains the priority que forwarding code
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
longest = [0,0,0,0] # store longest travel time of a packet:[low,mid,high,ultra]

# priority Que
class DataStructure:
    def __init__(self):
        self.que = []
        self.nextMid = 0        # holds location of the next insert for mid priority 
        self.nextHigh = 0        # holds location of the next insert for high priority 
        self.nextUltra = 0        # holds location of the next insert for ultra priority 
 
    # adds item to back of que if space exists
    def addPacket(self, packet):
    # only add low if there is room in the que
        if packet["priority"] == "LOW" and len(self.que) < QUE_SIZE:
            self.que.append(packet)
            # only add a mid priority if room in que behind other mids
        elif packet["priority"] == "MID" and self.nextMid < QUE_SIZE: 
            self.fullCheck()
            
            self.que.insert(self.nextMid, packet)
            self.nextMid +=1
        # if HIGH add behind other HIGHs if room to do so   
        elif packet["priority"] == "HIGH" and self.nextHigh< QUE_SIZE: 
            self.fullCheck()            

            self.que.insert(self.nextHigh, packet)
            self.nextMid +=1
            self.nextHigh +=1
            # if ULTRA and there is room for an ULTRA in the que add behind other ULTRAs
        elif packet["priority"] == "ULTRA" and self.nextUltra < QUE_SIZE: 
            self.fullCheck()        

            self.que.insert(self.nextUltra, packet)
            self.nextMid +=1
            self.nextHigh +=1 
            self.nextUltra +=1
        else: # packet is "lost"
            self.packetLossCounter(packet) 
            
    # check to see if the list is full and if so drop last item in the que (lowest priority)
    def fullCheck(self):
        if len(self.que) >= QUE_SIZE:
            rem = self.que[QUE_SIZE-1]
            # keep respective priorities nexts from going above QUE_SIZE
            if rem["priority"] == "MID":
                self.nextMid -= 1                        
            elif rem["priority"] == "HIGH":
                self.nextHigh -= 1
            elif rem["priority"] == "ULTRA":
                self.nextUltra -= 1    
            self.que.pop(QUE_SIZE-1)
            self.packetLossCounter(rem)
        
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
    def updateLongest(i, time):
        global longest
        
        
        
    # return the first packet in the list  
    def getTop(self):
        toReturn = self.que[0]
        self.removePacket()
        return toReturn

        # remove the first packet in the list      
    def removePacket(self):
        if len(self.que) > 0:
            rem = self.que[0] # the removed packet
            self.que.pop(0)
            
            # update to insert next pointers
            # the higher the priority removed the more the pointer changes
            if rem["priority"] == "MID": 
                self.nextMid -= 1      
            elif rem["priority"] == "HIGH": 
                self.nextMid -= 1 
                self.nextHigh -= 1 
            elif rem["priority"] == "ULTRA": 
                self.nextMid -= 1 
                self.nextHigh -= 1 
                self.nextUltra -= 1
    def getSize(self):
        return len(self.que)           
# print the amount of packets lost for each priority class
def printLostPackets():
    print("Low dropped: " + str(lostPackets[0]))
    print("Mid dropped: " + str(lostPackets[1]))        
    print("High dropped: " + str(lostPackets[2]))
    print("Ultra dropped: " + str(lostPackets[3]))