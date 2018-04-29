const HuhulaSale = artifacts.require("./HuhulaToken.sol")

module.exports = function(deployer, network, accounts) {
  deployer.deploy(HuhulaSale);
};
