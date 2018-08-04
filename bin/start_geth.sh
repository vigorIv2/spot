#!/bin/bash
geth --rinkeby --rpc --rpcapi db,eth,net,web3,personal --syncmode fast --cache 1024 --datadir /mnt/vol1/ethereum --ipcpath /mnt/vol1/ethereum/geth.ipc 

