This project contains code implementing four different packet forwarding approaches and
prints statistics based on each approaches performance.

The sender sends messages to the router
The router implements the forwarding approach and prints how many packets were dropped
The reciever recieves packets from the router and prints out stats about their journey


To run on the command line (3 terminals needed):

First: have all componenets in the same file
you should have a:
	sender.py
	reciever.py
	router.py
	fifo.py
	roundRobin.py
	reservedRR.py
	priorityQue.py

Second: start the reciever with python 3: python(3) reciever.py
Third: start the router with a forwarding approach on the same host:
	python(3) router.py rerr
		rerr: for the reserved round robin approach
		re: for the round robin approach
		pq: for the priority que approach
		fifo: for the first in first out approach
		Any other (or the lack of) input will break the code and you will need to restart the running process
Fourth: start the sender on the same host as the other 2 with: 
	python(3) sender.py
		if you want to change the number of packets send change the PACKETS_NUM constant
		the default is 500.

Approaches:

fifo: sends recieved packets in a fifo manner, dropping any recieved when the que is full.

priority Que: stores the packets in a priority que, dropping the lowest priority to make room 
	for a higher priority.

round robin: accepts packets in a fifo manner, but sends priority based on a rotation
	first a low packet, then a mid, then a high , then an ultra is sent then a low again.
	when none of a class exists it's turn is skipped.

reserved round robin: a mix of priority que and round robin.
	partly inspired by the weighted fair queing approach.
	each priority has reserved que space that is always availible for that priority.
	a packet is only dropped if a que is full and the reserved space for that packets priority class
	is full.
	if the que is full and there is reserved room for a new packet, a packet of a different 
	priority is dropped.
	This helps ensure for the lower priorities there is always a packet availible to send, while 
	higher priorities are given more favourable treatment with larger reserved spaces.
	