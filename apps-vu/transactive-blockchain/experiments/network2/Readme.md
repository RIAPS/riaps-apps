disable riaps-deplo.service on a node
```sudo systemctl stop riaps-deplo.service
```

on that node start riaps_deplo and log to a file
```sudo -E riaps_deplo | tee node.log
```

on vm node start riaps_deplo and log to a file
```/home/riaps/projects/riaps/riaps-apps/apps-vu/transactive-blockchain/Demo$ source ./test.sh
```

start blockchain
```/home/riaps/projects/riaps/riaps-apps/apps-vu/transactive-blockchain/Demo$ make startBC
```

start application
```/home/riaps/projects/riaps/riaps-apps/apps-vu/transactive-blockchain/Demo$ source ./tmux-launch.sh
```

unplug and replug network cable as many times as desired

collect logs

parse logs
