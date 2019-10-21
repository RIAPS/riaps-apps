#!/bin/sh
#TMUX PARAMETERS
riapsctl=0
miner=1
recorder=2
solver=0
dso=1
t101=2
t106=3

source .env

#APP PARAMETERS
echo $SOLVER
echo $MINER
echo $PORT
echo $RECORDER
echo $DSO
echo $T101
echo $T106
echo ${BBBs[@]}

echo $PASS

echo $PASS | sudo -E -S riaps_deplo | tee -a $EXPERIMENTS/deplo.log
