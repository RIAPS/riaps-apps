#!/bin/sh
tmux new -d -s grafana
tmux send-keys -t grafana 'cd /home/riaps/go/src/github.com/grafana/grafana' C-m
tmux send-keys -t grafana 'cd /home/riaps/go/src/github.com/grafana/grafana' C-m
tmux send-keys -t grafana './bin/linux-amd64/grafana-server' C-m
