include .env
startBC:
	# cd $(GETH) ; ./geth --datadir eth/  init genesis-data.json
	# cd $(GETH) ; ./geth account new --password password.txt --datadir eth/
	cd $(GETH); ./geth --datadir eth/ --rpc --rpcport 10000 --rpcaddr $(CTRL) --nodiscover --rpcapi 'eth,web3,admin,miner,net,db' --password password.txt --unlock 0 --networkid 15 --mine --minerthreads=1 --etherbase=0 --targetgaslimit 200000000000000000 console


initBC:
	tmux new -d -s geth
	tmux send -t geth "cd $(GETH)" ENTER
	tmux send -t geth "./geth account new --password password.txt --datadir eth/" ENTER
	tmux send -t geth "./geth --datadir eth/  init genesis.json" ENTER
