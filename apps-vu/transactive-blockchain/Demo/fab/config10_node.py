import fabric.api as fabi
import os
from dotenv import load_dotenv
load_dotenv()

USER=os.getenv('USER')
PASS=os.getenv('PASS')
SSHKEY=os.getenv('SSHKEY')
SSHPORT=os.getenv('SSHPORT')

print(os.getenv('BBBs'))
BBBs=os.getenv('BBBs')[1:-1].split(" ")
# print(type(BBBs))
# print(BBBs)

CTRL=os.getenv('CTRL')
ALL=BBBs+[CTRL]
print(ALL)

fabi.env.roledefs = {
    'BBBs': BBBs,
    'CTRL': CTRL,
	'ALL' : ALL,
}
