#!/bin/bash
source .env

pkill python3
pkill geth
tmux kill-server
#tmux kill-session -a
#tmux kill-session -t miner
pkill xterm
pkill sleep
sudo pkill -SIGKILL redis

fab -f fab/fabfile.py -R ALL kill:TransactiveEnergy
fab -f fab/fabfile.py -H localhost kill:TransactiveEnergy
fab -f fab/fabfile.py -R ALL restartDeplo




#fab -R all reset
