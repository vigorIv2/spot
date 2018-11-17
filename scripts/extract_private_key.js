#!/usr/bin/env node
var keyth=require('keythereum')


var keyobj=keyth.importFromFile('0x48ecad263eb6042fc84aA037A2F11832c9AA757A','/Users/ivasilchikov/Library/Ethereum/rinkeby')
var privateKey=keyth.recover('21641Canada',keyobj) //this takes a few seconds to finish

console.log("private key:"+privateKey.toString('hex'))
