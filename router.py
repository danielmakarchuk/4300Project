#Daniel makarchuk 7858045
#Professor: Sara Rouhani 
#4300
#this file contains the router forwarding packets to the reciever
# the program takes as input the desired forwarding strategy
# pq for priority que, rr for round robin
# rerr for reserved round robin, fifo for first in first out
import socket
import sys
import select
import json
import time
import random
import pdb

import reservedRR
import roundRobin
import fifo
import priorityQue

method = sys.argv[1]
sendMethod = None
# depending on the input choose the appropriate method to use
if method.lower() == "fifo":
    sendMethod = fifo.DataStructure() 
elif method.lower() == "pq":
    sendMethod = priorityQue.DataStructure() 
elif method.lower() == "rr":
    sendMethod = roundRobin.DataStructure() 
elif method.lower() == "rerr":
    sendMethod = reservedRR.DataStructure()     
else:
    print("Error, unrecognized method")
TIME_INTERVAL = 0.1 # send a packet ever 0.1 seconds


statPacket = {}# to store the stats packet


# socket to listen for incomming packets
       
hostname = socket.gethostname()# use local hostname as host
port = 8000

# reciever socket, to send to.
hostnameRec = socket.gethostname()# use local hostname as host
portRec = 8001

myClients = [] #holds connected sockets

routersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
routersocket.bind((socket.gethostname(), port))
routersocket.listen()

currTime = time.time()

do = True # if true continue socket loop
statsRec = False # holds whether or not the stats packet has been recieved

sendingsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:# try to connect to router
    sendingsocket.connect((hostnameRec, portRec))
except Exception as e:
    print("Something happened when connecting to reciever. program stopped")
    print(e)
    sys.exit(0)
# infastructure to send to reciever
def doSend (packet):
    try:
        sending = (json.dumps(packet)).encode()
        sendingsocket.sendall(sending)
    except Exception as e:
        print("Something happened when sending to reciever")
        print(e)
        #try to send a packet, only if the que is not empty
def trySend():
    if sendMethod.getSize() > 0:
        toSend = sendMethod.getTop()
        doSend(toSend)
    elif statsRec: # if que empty and stats recieved is true set do to false
        global do
        do = False
        doSend(statPacket)
    
# do appropriate action based on stats       
def processPack(packet):
    if packet["priority"] == "STAT":
        global statsRec
        global statPacket
        statsRec = True
        statPacket = packet #store the stats packet
    else:
        sendMethod.addPacket(packet)   
        # the socket loop, stopped after the last packet is recieved
while do:
    try:
        readable, writable, error = select.select([routersocket, ] + myClients, [], [])

        for aSocket in readable:
            if aSocket == routersocket:
                conn, addr = routersocket.accept()
                conn.setblocking(False)
                myClients.append(conn)
            else: # must be in a client socket
                data = aSocket.recv(1024)
                if data:
                    strData = data.decode('utf-8')
                    packet = json.loads(strData)
                    processPack(packet)

        # send packet on only if TIME_INTERVAL time has passed
        if time.time() > (currTime + TIME_INTERVAL):
            #do send
            trySend()
            currTime = time.time() 
    except socket.error as e:
        print("Socket Error.  troubled socket removed from server")
        myClients.remove(aSocket) # remove trouble socket when it disconnects
        print(e)
    except TimeoutError as e:
        pass
    except socket.timeout as e:
        pass
    except KeyboardInterrupt as e:
        print("Program ended via interrupt")
        sys.exit(0)
    except Exception as e:
        print("Something happened.  program stopping")
        print(e)
        sys.exit(0)
# print appropriate router stats
if method.lower() == "fifo":
    fifo.printLostPackets() 
elif method.lower() == "pq":
    priorityQue.printLostPackets() 
elif method.lower() == "rr":
    roundRobin.printLostPackets() 
elif method.lower() == "rerr":
    reservedRR.printLostPackets()    
print("\nProcessing Over")