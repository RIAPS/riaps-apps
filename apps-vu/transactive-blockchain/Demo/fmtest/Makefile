include .env
startBC:
	# cd $(GETH) ; ./geth --datadir eth/  init genesis-data.json
	# cd $(GETH) ; ./geth account new --password password.txt --datadir eth/
	cd $(GETH); ./geth --datadir eth/ --rpc --rpcport 10000 --rpcaddr $(CTRL) --nodiscover --rpcapi 'eth,web3,admin,miner,net,db' --password password.txt --unlock 0 --networkid 15 --mine --targetgaslimit 200000000000000000 console
