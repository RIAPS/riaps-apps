import sys
import glob, os
import time,datetime
import numpy as np
from operator import sub

# inject node
# detected trader 101 nic is down/up
# peer notified
# trader 106 notified

injectDown=[]
injectUp=[]
tradernotified=[]
peerDownNofify=[]
peerUpNofify=[]

def timeDiff(l1,l2):
    # l2 - l1
    diff = list(map(sub, l2,l1))
    diff_s = list(map(lambda x: x.total_seconds(), diff))
    return diff_s

off = False
for filename in glob.glob("*.log"):
    # print(filename)
    with open(filename) as fp:
        lines = fp.readlines()
        for line in lines:
            #fault injected on node
            if "state has changed (DOWN" in line:
                time = line[5:17]
                injectDown.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                # print("nicmon Down: %s" %time)
            #faulty trader notified
            elif "state has changed (UP" in line:
                time = line[5:17]
                injectUp.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                # print("nicmon UP: %s" %time)
            #faulty trader notified
            elif "NIC is up" in line:
                time = line[8:20]
                tradernotified.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                # print("trader up: %s" %time)
                # print(line)
            elif "23A27CD69D34E53CA3056C77A959E5C9, STATE: off" in line and "22:06:47,473" not in line:
                off = True
                time = line[53:65]
                peerDownNofify.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                # print(line)
                # print("peerDown: %s" %time)
            elif "23A27CD69D34E53CA3056C77A959E5C9, STATE: on" in line:
                if off:
                    off = False
                    time = line[53:65]
                    peerUpNofify.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                    # print(line)
                    # print("peerUp: %s" %time)
            elif "EXIT" in line and "172.21.20.47" in line:
                pass
                #do if there is time.
                #time to notify 

# print(len(peerUpNofify))
# for ix, i in enumerate(peerDownNofify):
#     print("inject: %s" %injectDown[ix].strftime("%H:%M:%S,%f"))
#     print("notify: %s" %peerDownNofify[ix].strftime("%H:%M:%S,%f"))

time2notifyPeerDown = timeDiff(injectDown, peerDownNofify)
# print(time2notifyPeerDown)

time2notifySelf = timeDiff(injectUp, tradernotified)
# print(time2notifySelf)

time2notifyPeerUp = timeDiff(injectUp, peerUpNofify)
# print(time2notifyPeerUp)

file1=open("peerDown.csv","w")
file1.write("peerDown\n")
file2=open("selfUp.csv","w")
file2.write("selfUp\n")
file3=open("peerUp.csv","w")
file3.write("peerUp\n")

for time in time2notifyPeerDown:
    print("peerDown;"+str(time))
    file1.write(str(time)+"\n")

for time in time2notifySelf:
    print("selfUp;"+str(time))
    file2.write(str(time)+"\n")

for time in time2notifyPeerUp:
    print("peerUp;"+str(time))
    file3.write(str(time)+"\n")
