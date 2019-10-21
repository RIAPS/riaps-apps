import fabric.api as fabi
import os
import dotenv
path = dotenv.find_dotenv('.env', usecwd=True)
dotenv.load_dotenv(path)
path = dotenv.find_dotenv('.myenv', usecwd=True)
dotenv.load_dotenv(path)

USER=os.getenv('USER')
PASS=os.getenv('PASS')
SSHKEY=os.getenv('SSHKEY')
SSHPORT=os.environ.get('SSHPORT')

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
