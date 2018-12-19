pragma solidity ^0.5.0;

import "openzeppelin-solidity/contracts/token/ERC20/CappedToken.sol";
import "openzeppelin-solidity/contracts/token/ERC20/PausableToken.sol";
import "openzeppelin-solidity/contracts/token/ERC20/BurnableToken.sol";

/**
* Huhula - spot location token
*/
contract HuhulaToken is CappedToken(700000000000000), PausableToken(), BurnableToken() {
  string public name = "Huhula spot token";
  string public symbol = "HUHU";
  uint256 public decimals = 6;

  constructor(string memory tokenName, string memory tokenSymbol) public {
	  name = tokenName;
	  symbol = tokenSymbol;
  }

  /**
    To return tokens to owner, main use case buyback scenario  
  */  
  function huhulaReturnToOwner(address _from, uint256 _value) public {
    require(owner != address(0));
    require(_from != owner);
    require(_value <= balances[_from]);

    balances[_from] = balances[_from].sub(_value);
    balances[owner] = balances[owner].add(_value);
    emit Transfer(_from, owner, _value);
  }

  /**
    * @dev Override MintableTokenn.finishMinting() to add canMint modifier
  */
  function finishMinting() onlyOwner canMint public returns(bool) {
      return super.finishMinting();
  }
  
}
