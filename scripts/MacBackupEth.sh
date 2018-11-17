#!/bin/bash
todaysdate=`date +%Y%m%d`
mkdir -p ~/Desktop/BackupETH/$todaysdate/keystore
mkdir -p ~/Desktop/BackupETH/$todaysdate/rinkeby/keystore
cp -r ~/Library/Ethereum/rinkeby/keystore ~/Desktop/BackupETH/$todaysdate/rinkeby/
cp -r ~/Library/Ethereum/keystore ~/Desktop/BackupETH/$todaysdate/

pushd `pwd`
MD="${HOME}/Library/Application Support/Mist"
if [ -d "$MD" ] ; then
  cd "$MD"
  zip  ~/Desktop/BackupETH/$todaysdate/Mist_no_swarm_no_binaries.zip . -r -9 -x "swarmjs/*" -x "binaries/*"
fi
ED="${HOME}/Library/Application Support/Ethereum Wallet"
if [ -d "$ED" ] ; then
  cd "$ED"
  zip  ~/Desktop/BackupETH/$todaysdate/Ethereum_Wallet_no_swarm_no_binaries.zip . -r -9 -x "swarmjs/*" -x "binaries/*"
fi
popd


echo "Do not forget to record the content of ~/Desktop/BackupETH/$todaysdate to DVD, then ship it to 'safe heaven'"
sleep 5s

