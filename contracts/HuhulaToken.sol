pragma solidity ^0.4.18;

import "zeppelin-solidity/contracts/token/ERC20/CappedToken.sol";
import "zeppelin-solidity/contracts/token/ERC20/PausableToken.sol";

/**
* Huhula - Parking location token
*/
contract HuhulaToken is CappedToken(HuhulaToken.HUHULA_HARD_CAP), PausableToken() {
  string public name = "Huhula park token";
  string public symbol = "HUHU";
  uint256 public decimals = 6;
  uint256 public constant HUHULA_HARD_CAP = 1000000000000000000; // 1 Bil with 6 decimals

  function HuhulaToken(string tokenName, string tokenSymbol) public {
	  name = tokenName;
	  symbol = tokenSymbol;
  }

  function approveSpender(address _holder, address _spender, uint256 _value) public returns (bool) {
    allowed[_holder][_spender] = _value;
    Approval(_holder, _spender, _value);
    return true;
  }

}
