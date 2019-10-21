import sys
import glob, os
import time,datetime
import numpy as np
from operator import sub

# inject node
# detected trader 101 nic is down/up
# peer notified
# trader 106 notified

injected=[]
tradernotified=[]

for filename in glob.glob("*.log"):
    print(filename)
    with open(filename) as fp:
        lines = fp.readlines()
        for line in lines:
            #fault injected on node
            if "state has changed (DOWN" in line:
                time = line[5:17]
                injected.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                print("nicmon Down: %s" %time)
                # print(time)
                # print(injected)
            #faulty trader notified
            elif "state has changed (UP" in line:
                time = line[5:17]
                injected.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                print("nicmon UP: %s" %time)
                # print(time)
                # print(injected)
            #faulty trader notified
            elif "NIC is down" in line:
                time = line[8:20]
                tradernotified.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                print("trader down: %s" %time)
                # print(line)
                # print(notified)
            elif "NIC is up" in line:
                time = line[8:20]
                tradernotified.append(datetime.datetime.strptime(time, "%H:%M:%S,%f"))
                print("trader up: %s" %time)
                # print(line)


# print(injected)
# print(tradernotified)
# time2notifySelf = list(map(sub, tradernotified,injected))
# print(list(map(lambda x: x.total_seconds(), time2notifySelf)))




            # if "riaps.deplo.fm" in line and \
            #     "172.21.20.47" in line :
            #     print(line)
            #     time = line[5:17]
            #     detected = datetime.datetime.strptime(time, "%H:%M:%S,%f")
            #     # print(detected)
            # elif "EXIT" in line and \
            #     "172.21.20.47" in line :
            #     print(line)
            #     time = "20"+line[3:20]
            #     print(time)
            #     detected = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            #     # print(detected)
            #
            # if "DOWN" in line:
            #     print(line)
            #     time = line[5:17]
            #     injected = datetime.datetime.strptime(time, "%H:%M:%S,%f")
            #     print(injected)
            # if "UP" in line:
            #     print(line)
            #     time = line[5:17]
            #     injected = datetime.datetime.strptime(time, "%H:%M:%S,%f")
            #     print(injected)
