#Daniel makarchuk 7858045
#Professor: Sara Rouhani 
#4300
#this file contains the reserved round robin components
# in this a portion of the que is always open to a priority
# it is inspired by the weighted fair queing with weights being 
#given to the minimum spaces for a priority
# it uses round robin for packet delivery
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

LOW_WEIGHT = 3
MID_WEIGHT = 4
HIGH_WEIGHT = 5
ULTRA_WEIGHT = 8
WEIGHTS = [3,4,5,8] # array containing priority weights index 0 = low, 1 = mid, 2 = high, 3 = ultra


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
    # only add if there is room in the appropriate que
        # add to lowQue if low priority and there is room in the que, or there is reserved low room 
        if packet["priority"] == "LOW" and (len(self.ques[LOW]) < LOW_WEIGHT or self.size < QUE_SIZE):
            self.removeAsNeeded(LOW)            
            self.ques[LOW].append(packet)
            self.size +=1 # update size
        elif packet["priority"] == "MID" and (len(self.ques[MID]) < MID_WEIGHT or self.size < QUE_SIZE): 
            self.removeAsNeeded(MID)   
            self.ques[MID].append(packet) 
            self.size +=1 # update size
        elif packet["priority"] == "HIGH" and (len(self.ques[HIGH]) < HIGH_WEIGHT or self.size < QUE_SIZE):           
            self.removeAsNeeded(HIGH)            
            self.ques[HIGH].append(packet)
            self.size +=1 # update size
        elif packet["priority"] == "ULTRA" and (len(self.ques[ULTRA]) < ULTRA_WEIGHT or self.size < QUE_SIZE):       
            self.removeAsNeeded(ULTRA)            
            self.ques[ULTRA].append(packet)
            self.size +=1 # update size
        else: # packet is "lost"
            self.packetLossCounter(packet) 
            
    # removes a packet from a que to make room for another packet when the Que is full
    def removeAsNeeded(self, priority):
    #only remove if needed
        if self.size >= QUE_SIZE:
            i = 0 # by starting at 0 this ensures first low priority packets are attempted to be dropped
            while i < len(self.ques):
                # do not remove if of the priority room is being made for, 
                #nor if the priority to be removed only has items in reserved space
                if not (priority == i or WEIGHTS[i] >= len(self.ques[i])):
                    # drop last item from priority i's que
                    self.packetLossCounter(self.ques[i][len(self.ques[i])-1])
                    self.ques[i].pop()
                    self.size -=1 # update size
                i +=1
        
    
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