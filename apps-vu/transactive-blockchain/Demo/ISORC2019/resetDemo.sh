#!/bin/bash
source .env

pkill python3
# pkill geth
tmux kill-server
#tmux kill-session -a
#tmux kill-session -t miner
pkill xterm
pkill sleep
sudo pkill -SIGKILL redis

fab -f fab/fabfile.py -R ALL pkill:TransactiveEnergy
fab -f fab/fabfile.py -H localhost kill:TransactiveEnergy
fab -f fab/fabfile.py -R BBBs restartDeplo
fab -f fab/fabfile.py -R BBBs prunCommand:"sudo rm /tmp/*.log"




#fab -R all reset
