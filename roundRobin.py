#Daniel makarchuk 7858045
#Professor: Sara Rouhani 
#4300
#this file contains the round robin forwarding code
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
LOW = 0
MID = 1
HIGH = 2
ULTRA = 3



#This data structure is a multi que one where the each priority has its own que
#it returns packets in a round robin approach
# the space is allocated first come first serve
class DataStructure:
    def __init__(self):
        self.ques = [[],[],[],[]] # [[lowQue],[midQue],[highQue],[ultraQue]]    
        self.size = 0
        self.roundNum = 0 # round num used to determin which que gets sent from
 
    # adds item to appropriate que if space exists
    # Fifo used for que storage
    def addPacket(self, packet):
    # only add if there is room in the que
        if self.size < QUE_SIZE:
            self.size +=1 # update size
            # add to lowQue if low priority  
            if packet["priority"] == "LOW":
                self.ques[LOW].append(packet)
            elif packet["priority"] == "MID": 
                self.ques[MID].append(packet) 
            elif packet["priority"] == "HIGH":           
                self.ques[HIGH].append(packet)
            elif packet["priority"] == "ULTRA":       
                self.ques[ULTRA].append(packet)
        else: # packet is "lost"
            self.packetLossCounter(packet) 
        
    # adds to the tracking variable lostPackets appropriatly when called      
    def packetLossCounter(self, packet):
        if packet["priority"] == "LOW":
            lostPackets[0] +=1
        elif packet["priority"] == "MID": 
            lostPackets[1] +=1        
        elif packet["priority"] == "HIGH": 
            lostPackets[2] +=1 
        else: # if not any other priority it must be ULTRA
            lostPackets[3] +=1 
    # return the appropriate packet via round robin
    def getTop(self):
        ret = None
        # only enter loop if there is something to return
        if not self.size == 0:
            while not ret:
                ret = self.getNext()
            self.size -=1 # reduce size by one since getnext will remove an item
        return ret
    #return a packet based on roundRobin
    def getNext(self):
        toReturn = None
        #if an item in roundNum que, set toReturn to the first que value and remove the first value
        if (len(self.ques[self.roundNum]) > 0):
            toReturn = self.ques[self.roundNum][0]
            self.ques[self.roundNum].pop(0)
        # update round num
        if self.roundNum == ULTRA:
            self.roundNum -=3 # update round num, -3 to bring it back to 0   
        else:
            self.roundNum += 1
        return toReturn  
        # return the amount of packets in the multi que data structure
    def getSize(self):
        return self.size
            
# print the amount of packets lost for each priority class
def printLostPackets():
    print("Low dropped: " + str(lostPackets[0]))
    print("Mid dropped: " + str(lostPackets[1]))        
    print("High dropped: " + str(lostPackets[2]))
    print("Ultra dropped: " + str(lostPackets[3]))