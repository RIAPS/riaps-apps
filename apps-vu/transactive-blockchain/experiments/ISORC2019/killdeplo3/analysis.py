import sys
import glob, os
import time,datetime
import numpy as np
from operator import sub
import csv

# inject node
# detected trader 101 nic is down/up
# peer notified
# trader 106 notified

injectFault=[]
ActorNotify=[]
ActorTerminated=[]
peerLost=[]
cleanup=[]
ActorRecovered=[]
peerJoined=[]


def timeDiff(l1,l2):
    # l2 - l1
    diff = list(map(sub, l2,l1))
    diff_s = list(map(lambda x: x.total_seconds(), diff))
    return diff_s

for filename in glob.glob("*.log"):
    #print(filename)
    lost = False
    kill = False
    with open(filename) as fp:
        lines = fp.readlines()
        for line in lines:
            #fault injected on node
            if 'node' in filename:
                if "9/KILL" in line:
                    kill = True
                    time = line[7:15]
                    #print(time)
                    injectFault.append(datetime.datetime.strptime(time, "%H:%M:%S"))
                    #print(line)
                if kill:
                    if "stopping Trader" in line:
                        # ActorNotify
                        time = line[50:62]
                        #print(time)
                        ActorNotify.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                        #print(line)
                    elif "terminated Trader" in line:
                        # ActorTerminated
                        time = line[50:62]
                        #print(time)
                        ActorTerminated.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                        #print(line)
                    elif "recover: disco" in line:
                        # cleanup
                        time = line[50:62]
                        #print(time)
                        cleanup.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                        #print(line)
                    elif "Connected: 1" in line:
                        # ActorRecovered
                        kill = False
                        time = line[53:65]
                        #print(time)
                        ActorRecovered.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                        #print(line)
            if 'peer' in filename:
                if "peer-" in line:
                    # peerLost
                    time = line[50:62]
                    #print(time)
                    peerLost.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                    lost = True
                    #print(line)
                elif "peer+" in line:
                    # peerJoined
                    if lost:
                        time = line[50:62]
                        #print(time)
                        peerJoined.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                        #print(line)
                        lost = False


with open ("logs.csv", 'a') as csvfile:
    fieldnames = ['AN','AT','CU','AR','PL','PJ']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for ix, i in enumerate(ActorRecovered):
        diffAN = (ActorNotify[ix] - injectFault[ix]).total_seconds()
        diffAT = (ActorTerminated[ix] - ActorNotify[ix]).total_seconds()
        diffCU = (cleanup[ix] - ActorTerminated[ix]).total_seconds()
        diffAR = (ActorRecovered[ix] - cleanup[ix]).total_seconds()

        diffPL = (peerLost[ix] - injectFault[ix]).total_seconds()
        diffPJ = (peerJoined[ix] - injectFault[ix]).total_seconds()
        print(diffAN)
        print(diffAT)
        print(diffCU)
        print(diffAR)

        print(diffPL)
        print(diffPJ)
        row = {'AN':diffAN,
               'AT': diffAT,
               'CU':diffCU,
               'AR':diffAR,
               'PL':diffPL,
               'PJ':diffPJ}
        writer.writerow(row)
