b=(bbb-a702.local bbb-99b4.local bbb-1b70.local bbb-5eb7.local)

for i in "${!b[@]}"
do :

ssh ${b[i]} -p 2222  'pkill -SIGKILL riaps_device; pkill -SIGKILL riaps_devm; pkill -SIGKILL riaps_disco;  pkill -SIGKILL riaps_deplo;pkill -SIGKILL riaps_actor;pkill -SIGKILL tmux'

done
