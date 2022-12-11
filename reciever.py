#Daniel makarchuk 7858045
#Professor: Sara Rouhani 
#4300
#this file contains the reciever which recieves packets from the router
# It then stores the packet and later uses the packets to calculate and show stats

import socket
import sys
import select
import json
import time
import random
import pdb

priRec = [0,0,0,0]#tracks packets of each priority recieved, [low,mid,high,ultra]
packets = [] # store recieved Packets
statPacket = {}# to store the stats packet from the sender
do = True
timeDiff = 0 # time difference between sender and reciever
longest = [0,0,0,0] #stores longest time to arrive for each priority [low,mid,high,ultra]

#handles an arrived packet
#if not stats packet then add to packets list
def handlePacket(packet):
    if packet["priority"] == "STAT":
        global do
        global statPacket        
        statPacket = packet
        do = False
    elif packet["priority"] == "TIME": # calculate difference between sender and reciever time.time()
        global timeDiff
        timeDiff = (time.time() - packet["time"])
        print ("The time difference between reciever and sender is: " + str(timeDiff) + " seconds")
    else:
        packet["endTime"] = time.time() # the arrival time of a packet to the reciever
        packets.append(packet)
        priorityStats(packet) # update recieved stats
# update global priority counter based on priority level
def priorityStats(packet):
    if packet["priority"] == "LOW":
        priRec[0] +=1
    elif packet["priority"] == "MID": 
        priRec[1] +=1        
    elif packet["priority"] == "HIGH": 
        priRec[2] +=1 
    else: # if not anyother priority it must be ULTRA
        priRec[3] +=1   
# calculate average times for each priority arrived
def calcStats():
    averages = [0,0,0,0] # (low,mid,high,ultra)
    for each in packets:
        #time packet trip is end time - start time - time difference 
        #(if reciever time.time() more advanced than sender clock -timeDiff gives a more accurate time)
        packTime = (each["endTime"] - each["startTime"]) - timeDiff
        if each["priority"] == "LOW":
            averages[0] += packTime
            updateLongest(0, packTime)
        elif each["priority"] == "MID": 
            averages[1] += packTime   
            updateLongest(1, packTime)            
        elif each["priority"] == "HIGH": 
            averages[2] += packTime 
            updateLongest(2, packTime)                 
        else: # must be ultra, since it is the only priority left
            averages[3] += packTime 
            updateLongest(3, packTime)                 
    # calculate the average
    for i in range(len(averages)):
        if priRec[i] > 0: # prevent divide by zero
            averages[i] = averages[i]/priRec[i] 
            
    return averages
    
# if time longer than previous max for the priority i (0=low, 1 mid, 2 high, 3 ultra) update
def updateLongest(i, time):
    global longest
    longest[i] = max(longest[i], time)    
    
# print out the statistical values        
def printStats():
    print("Low recieved: " + str(priRec[0]) + " of " + str(statPacket["lowSent"]) + " sent")
    print("Mid recieved: " + str(priRec[1]) + " of " + str(statPacket["midSent"]) + " sent")        
    print("High recieved: " + str(priRec[2]) + " of " + str(statPacket["highSent"]) + " sent")
    print("Ultra recieved: " + str(priRec[3]) + " of " + str(statPacket["ultraSent"]) + " sent")
    averages = calcStats()    
    print("Low longest took: " + str(longest[0]))
    print("Mid longest took: " + str(longest[1]))        
    print("High longest took: " + str(longest[2]))
    print("Ultra longest took: " + str(longest[3]))

    print("Low average travel time: " + str(averages[0]))
    print("Mid average travel time: " + str(averages[1]))        
    print("High average travel time: " + str(averages[2]))
    print("Ultra average travel time: " + str(averages[3]))

#create  socket
hostname = socket.gethostname()# use local hostname as host
port = 8001

recieversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
recieversocket.bind((socket.gethostname(), port))
recieversocket.listen()
recieversocket.settimeout(5)

myClients = [] #holds connected sockets
# socket loop
while do:
    try:
        readable, writable, error = select.select([recieversocket, ] + myClients, [], [])

        for aSocket in readable:
            #Establish a connection
            if aSocket == recieversocket:
                conn, addr = recieversocket.accept()
                conn.setblocking(False)
                myClients.append(conn)
            else: # Read data from an established connection
                data = aSocket.recv(1024)
                if data:
                    strData = data.decode('utf-8')
                    packet = json.loads(strData)
                    handlePacket(packet)

    except socket.error as e:
        print("Socket Error.  troublesd socket removed from server")
        myClients.remove(aSocket) # remove trouble socket when it disconnects
        print(e)
    except TimeoutError as e:
        pass
    except socket.timeout as e:
        pass
    except KeyboardInterrupt as e:
        print("RIP")
        sys.exit(0)
    except Exception as e:
        print("Something happened when recieving socket.  stopping program")
        print(e)
        sys.exit(0)
printStats() # print the stats
print("\nProcessing Over")