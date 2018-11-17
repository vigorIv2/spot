#!/usr/bin/env node

const hdkey = require('ethereumjs-wallet/hdkey')
//const privateKey = hdkey.fromMasterSeed('random')._hdkey._privateKey
//console.log(privateKey)
const privateKey = Buffer.from("68688354ba9a942cb3145b6e624b3a9d147c8eb061be78eccc5e0777e77032af", "hex")
const Wallet = require('ethereumjs-wallet')
const wallet = Wallet.fromPrivateKey(privateKey)
console.log("public key:"+wallet.getPublicKeyString())
