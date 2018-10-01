#!/bin/bash
geth --rinkeby --rpc --rpcapi db,eth,net,web3,personal --syncmode fast --cache 1024 --datadir /mnt/vol1/ethereum --ipcpath /mnt/vol1/ethereum/geth.ipc --unlock="0xc58244edab7b794c5e9c8c33c8649f2cdfc90112" --password="/home/rock64/password_rinkeby.txt"

