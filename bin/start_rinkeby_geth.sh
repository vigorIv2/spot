#!/bin/bash
geth --rinkeby --rpc --rpcaddr `hostname -i` --rpcapi db,eth,net,web3,personal --syncmode fast --cache 1024 --datadir /mnt/vol1/ethereum/rinkeby --ipcpath /mnt/vol1/ethereum/rinkeby/geth.ipc --unlock="0xc58244edab7b794c5e9c8c33c8649f2cdfc90112" --password="/home/rock64/password_rinkeby.txt"

