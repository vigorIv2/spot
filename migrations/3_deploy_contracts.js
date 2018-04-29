const HuhulaSale = artifacts.require("./HuhulaSale.sol")

module.exports = function(deployer, network, accounts) {
  deployer.deploy(HuhulaSale);
};
