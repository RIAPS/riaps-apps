import sys
import glob, os
import time,datetime
import numpy as np
from operator import sub

# inject node
# detected trader 101 nic is down/up
# peer notified
# trader 106 notified

injectOff=[]
stopDM=[]
startDM=[]
stopTrader=[]
setupApp=[]
addActor=[]
startActor=[]
peerOffNofify=[]
peerOnNofify=[]
OffNofifyfm =[]
OnNofifyfm =[]


def timeDiff(l1,l2):
    # l2 - l1
    diff = list(map(sub, l2,l1))
    diff_s = list(map(lambda x: x.total_seconds(), diff))
    return diff_s

for filename in glob.glob("*.log"):
    print(filename)
    kill = False
    off = False
    stopped = False
    lost = False
    with open(filename) as fp:
        lines = fp.readlines()
        for line in lines:
            #fault injected on node
            if "9/KILL" in line:
                kill = True
                time = line[7:15]
                injectOff.append(datetime.datetime.strptime(time, "%H:%M:%S"))
                print("kill: %s" %time)
                pass
            elif "Stopping RIAPS Deployment Manager" in line:
                if not stopped and kill:
                    stopped = True
                    time = line[7:15]
                    # print(line)
                    stopDM.append(datetime.datetime.strptime(time, "%H:%M:%S"))
                    print("stop DM: %s" %time)
                    pass
            elif "Started RIAPS Deployment Manager Service" in line:
                if stopped and kill:
                    stopped = False
                    time = line[7:15]
                    startDM.append(datetime.datetime.strptime(time, "%H:%M:%S"))
                    print("start DM: %s" %time)
                    pass

            elif "stopping Trader" in line:
                if kill :
                    time = line[7:15]
                    stopTrader.append(datetime.datetime.strptime(time, "%H:%M:%S"))
                    print("stop trader time: %s" %time)
                    pass
            elif "setupApp TransactiveEnergy" in line:
                if kill :
                    time = line[7:15]
                    setupApp.append(datetime.datetime.strptime(time, "%H:%M:%S"))
                    print("setupApp: %s" %time)
                    pass
            elif "addActor TransactiveEnergy.Trader" in line:
                if kill :
                    time = line[7:15]
                    addActor.append(datetime.datetime.strptime(time, "%H:%M:%S"))
                    print("addActor: %s" %time)
                    pass
            elif "starting Trader" in line and "INFO" in line:
                if kill :
                    time = line[7:15]
                    startActor.append(datetime.datetime.strptime(time, "%H:%M:%S"))
                    print("starting Trader: %s" %time)
                    pass
            elif "STATE: off" in line:
                if not off:
                    off = True
                    time = line[7:15]
                    peerOffNofify.append(datetime.datetime.strptime(time, "%H:%M:%S"))
                    print("peerOffNofify: %s" %time)
                    pass
            elif "STATE: on" in line:
                if off:
                    off = False
                    time = line[7:15]
                    peerOnNofify.append(datetime.datetime.strptime(time, "%H:%M:%S"))
                    print("peerOnNofify: %s" %time)
                    pass
            elif "lost peer" in line:
                if not lost:
                    lost = True
                    time = line[5:17]
                    OffNofifyfm.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                    print("OffNofifyfm: %s" %time)
                    pass
            elif "has peer" in line:
                if lost:
                    lost = False
                    time = line[5:17]
                    OnNofifyfm.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                    print("OnNofifyfm: %s" %time)
                    pass











# print(len(peerUpNofify))
# for ix, i in enumerate(peerDownNofify):
#     print("inject: %s" %injectDown[ix].strftime("%H:%M:%S,%f"))
#     print("notify: %s" %peerDownNofify[ix].strftime("%H:%M:%S,%f"))

# time2notifyPeerDown = timeDiff(injectDown, peerDownNofify)
# # print(time2notifyPeerDown)
#
# time2notifySelf = timeDiff(injectUp, tradernotified)
# # print(time2notifySelf)
#
# time2notifyPeerUp = timeDiff(injectUp, peerUpNofify)
# # print(time2notifyPeerUp)
#
# file1=open("peerDown.csv","w")
# file1.write("peerDown\n")
# file2=open("selfUp.csv","w")
# file2.write("selfUp\n")
# file3=open("peerUp.csv","w")
# file3.write("peerUp\n")
#
# for time in time2notifyPeerDown:
#     print("peerDown;"+str(time))
#     file1.write(str(time)+"\n")
#
# for time in time2notifySelf:
#     print("selfUp;"+str(time))
#     file2.write(str(time)+"\n")
#
# for time in time2notifyPeerUp:
#     print("peerUp;"+str(time))
#     file3.write(str(time)+"\n")
