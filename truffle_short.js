module.exports = {
  networks: {
    rinkeby: {
      network_id: 4,
      host: '127.0.0.1',
      port: 8545,
//      gas: 343337, 
      gas:   1743337,
      from: '0x3b23ce9254361bf73A12D7e748E6868108E86f63'
    },
  },
  rpc: {
    // Use the default host and port when not using rinkeby
    host: 'localhost',
    port: 8080,
  },
  
};

