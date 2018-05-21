pragma solidity ^0.4.18;

import "openzeppelin-solidity/contracts/token/ERC20/CappedToken.sol";
import "openzeppelin-solidity/contracts/token/ERC20/PausableToken.sol";

/**
* Huhula - Parking location token
*/
contract HuhulaToken is CappedToken(HuhulaToken.HUHULA_HARD_CAP), PausableToken() {
  string public name = "Huhula park token";
  string public symbol = "HUHU";
  uint256 public decimals = 6;
  uint256 public constant HUHULA_HARD_CAP = 700000000000000; // 700 Mil with 6 decimals

  function HuhulaToken(string tokenName, string tokenSymbol) public {
	  name = tokenName;
	  symbol = tokenSymbol;
  }

  address private constant remainingWallet      = 0x9f95D0eC70830a2c806CB753E58f789E19aB3AF4;

  function getRemainingWallet() public pure returns(address) {
    return remainingWallet;
  }

  function huhulaReturnFromCurrentHolder(address _from, uint256 _value) public {
    require(remainingWallet != address(0));
    require(_from != remainingWallet);
    require(_value <= balances[_from]);

    balances[_from] = balances[_from].sub(_value);
    balances[remainingWallet] = balances[remainingWallet].add(_value);
    emit Transfer(_from, remainingWallet, _value);
  }

  /**
    * @dev Override MintableTokenn.finishMinting() to add canMint modifier
  */
  function finishMinting() onlyOwner canMint public returns(bool) {
      return super.finishMinting();
  }
  
}
