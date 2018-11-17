#!/bin/bash
hme=`pwd`
rm -rf ${hme}/build/*
truffle compile
for n in HuhulaSale HuhulaToken ; do
  jq .abi ${hme}/build/contracts/${n}.json > ${hme}/build/${n}.abi
  jq .bytecode ${hme}/build/contracts/${n}.json | sed 's/\"//g' > ${hme}/build/${n}.bin
  web3j solidity generate --javaTypes ${hme}/build/${n}.bin ${hme}/build/${n}.abi -p com.huhula.contract -o ${hme}/src/main/java/
done 
${hme}/scripts/importsub.py ${hme}/contracts/HuhulaSale.sol > ${hme}/build/HuhulaSale_all.sol
