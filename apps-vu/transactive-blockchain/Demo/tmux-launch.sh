#!/bin/sh
# -----------------------------------------------------------------------------------------------------
# This script lauches riaps_ctrl, the geth miner, and opens ssh connections to a few of the nodes that will have actors running on them.
# To run this script, from the command line enter : source ./tmux.sh
# -----------------------------------------------------------------------------------------------------

source .env

#TMUX PARAMETERS
riapsctl=0
miner=1
recorder=2
solver=0
dso=1
t101=2
t106=3

#APP PARAMETERS
# SOLVER=CTRL
# MINER=CTRL
# PORT=10000
# RECORDER=${arr[0]}
# DSO=${BBBs[1]}
# T101=${BBBs[2]}
# T106=${BBBs[3]}

# APP Cleanup
influx -execute 'drop database RIAPSEnergyMarket'
#sudo rm -rf /tmp/tmp*

tmux new-session -s transRiapsDemo -n env -d
tmux set -g pane-border-status top
tmux split-window -h
tmux split-window -h
tmux select-layout tiled

tmux new-window -n app
# tmux select-window -t app
tmux split-window -h
tmux split-window -h
tmux split-window -h
tmux select-layout tiled

tmux select-pane -t env.$riapsctl -T "RIAPSCTRL"
tmux send-keys -t env.$riapsctl "cd $DIR/$PROJECT/pkg" C-m
tmux send-keys -t env.$riapsctl "riaps_ctrl" C-m

tmux select-pane -t env.$miner -T "MINER"
tmux send-keys -t env.$miner "cd $GETH" C-m
tmux send -t env.$miner "pwd ; ./geth --datadir eth/  init genesis-data.json" ENTER
tmux send -t env.$miner "./geth account new --password password.txt --datadir eth/" ENTER
sleep 5
tmux send -t env.$miner "./geth --datadir eth/ --rpc --rpcport $PORT --rpcaddr $MINER --nodiscover --rpcapi 'eth,web3,admin,miner,net,db' --password password.txt --unlock 0 --networkid 15 --mine |& tee miner.out" ENTER

tmux select-pane -t env.$recorder -T "Recorder"
tmux send-keys -t env.$recorder "ssh -p $SSHPORT -i $SSHKEY $RECORDER" C-m
tmux send-keys -t env.$recorder 'sudo journalctl -f -u riaps-deplo.service --since "10 min ago"' C-m
#


tmux select-pane -t app.$solver -T "Solver"
tmux send-keys -t app.$solver "echo '$PASS' | sudo -E -S riaps_deplo" C-m
#

tmux select-pane -t app.$dso -T "DSO"
tmux send-keys -t app.$dso "ssh -p $SSHPORT -i $SSHKEY $DSO" C-m
tmux send-keys -t app.$dso 'sudo journalctl -f -u riaps-deplo.service --since "10 min ago"' C-m
#

tmux select-pane -t app.$t101 -T "Trader 101"
tmux send-keys -t app.$t101 "ssh -p $SSHPORT -i $SSHKEY $T101" C-m
tmux send-keys -t app.$t101 'sudo journalctl -f -u riaps-deplo.service --since "10 min ago"' C-m
#

tmux select-pane -t app.$t106 -T "Trader 106"
# tmux send-keys -t app.$t106 "sshpass -p 'riaps' ssh $T106" C-m
tmux send-keys -t app.$t106 "ssh -p $SSHPORT -i $SSHKEY $T106" C-m
tmux send-keys -t app.$t106 'sudo journalctl -f -u riaps-deplo.service --since "10 min ago"' C-m
# tmux send-keys -t app.$t106 'sudo journalctl -f -b -u riaps-deplo.service > pre.log' C-m

#

tmux attach -t transRiapsDemo
