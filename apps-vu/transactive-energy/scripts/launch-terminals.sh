b=(bbb-a702.local bbb-99b4.local bbb-1b70.local bbb-5eb7.local)
x=(600 1200 600 1200)
y=(150 600 600 150)

xterm -geometry 93x31+0+${y[0]} -hold -e rpyc_registry.py &
sleep 1
xterm -geometry 93x31+0+${y[1]} -hold -e riaps_ctrl &
sleep 1
xterm -hold -e 'cd ../grunner-project/ && python3 riaps_grunner.py' &

for i in "${!b[@]}"
do :
xterm -geometry 93x31+${x[i]}+${y[i]} -hold -e ssh ${b[i]} -p 2222 &
ssh -t ${b[i]} -p 2222 'tmux new -d -s deplo'
ssh -t ${b[i]} -p 2222 'tmux send -t deplo.0 riaps_deplo ENTER'
done

#reminder of how to check tmux: ssh -t i -p 2222 'tmux attach -t deplo'
