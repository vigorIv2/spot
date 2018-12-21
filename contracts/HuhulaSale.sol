pragma solidity ^0.4.24;

import './HuhulaToken.sol';
import "openzeppelin-solidity/contracts/math/SafeMath.sol";

import "openzeppelin-solidity/contracts/ownership/Ownable.sol";
import "openzeppelin-solidity/contracts/crowdsale/validation/TimedCrowdsale.sol";
import "openzeppelin-solidity/contracts/lifecycle/Pausable.sol";

/**
  Huhula crowdsale
*/
                                                                                     
contract HuhulaSale is Ownable, TimedCrowdsale(block.timestamp + 1, block.timestamp + 1 + 10368000), Pausable {
  using SafeMath for uint256;

//**********************************************************************************************
// ------------------------------ Customize Smart Contract ------------------------------------- 
  uint32 public buyBackRate = 1034; // in ETH with 6 decimal places per token, initially 0.001034
//**********************************************************************************************
  uint256 public minLotSize = 5 ether; 

  constructor() public 
    Crowdsale(23356, 0xa4aA1C90f02265d189a96207Be92597fFEaD54D2, new HuhulaToken("Huhula spot","HUHU") ) {
  }

  function calcTokens(uint256 weiAmount) internal view returns(uint256) {
    // calculate token amount to be sent to buyer
    uint256 tokens = weiAmount.mul(rate).mul(1000000).div(1 ether).div(100);
    uint256 tokensLeft = HuhulaToken(token).cap().sub(token.totalSupply());
    if ( tokensLeft < tokens ) {
      tokens = tokensLeft;
    }
    return tokens;
  }

  // Events
  event SpenderApproved(address indexed to, uint256 tokens);
  event GrantTokens(address indexed to, uint256 tokens);
  event RewardTokens(address indexed to, uint256 tokens);
  event RateChange(uint256 rate);

  /**
  * @dev Sets HUHU to Ether rate. Will be called multiple times durign the crowdsale to adjsut the rate
  * since HUHU cost is fixed in USD, but USD/ETH rate is changing
  * @param paramRate defines HUHU/ETH rate: 1 ETH = paramRate HUHUs
  */
  function setRate(uint256 paramRate) public onlyOwner {
    require(paramRate >= 1);
    rate = paramRate;
    emit RateChange(paramRate);
  }

  function setMinLotSize(uint256 paramLot) public onlyOwner {
    require(paramLot >= 1 finney);
    minLotSize = paramLot;
  }

  // fallback function can be used to buy tokens
  function () external payable {
    buyTokens(msg.sender);
  }

  // low level token purchase function
  function buyTokens(address beneficiary) public whenNotPaused payable {
    require(beneficiary != address(0));
    require(block.timestamp <= closingTime);       

    uint256 weiAmount = msg.value;
    require(weiAmount >= minLotSize);

    // calculate token amount to be created
    uint256 tokens = calcTokens(weiAmount);

    // update state
    weiRaised = weiRaised.add(weiAmount);
    if ( HuhulaToken(token).mint(beneficiary, tokens) ) {
      emit TokenPurchase(address(0x0), beneficiary, weiAmount, tokens);
      forwardFunds();
    }
  }

  /**
    Function to grant some tokens to early testers before or during crowdsale
  */
  function grantTokens(address beneficiary,uint256 tokens) public onlyOwner {
    require(beneficiary != address(0));
    require(block.timestamp <= closingTime);                         

    if ( HuhulaToken(token).mint(beneficiary, tokens) ) {
      emit GrantTokens(beneficiary, tokens);
    }
  }

  // send ether to the fund collection wallet
  // override to create custom fund forwarding mechanisms
  function forwardFunds() internal {
    wallet.transfer(msg.value);
  }
  
  /**
  * @dev Allows to resume crowdsale 
  */
  function resume(uint256 _hours) public onlyOwner {
    require(_hours <= 744); // shorter than longest month, i.e. max one month
    require(_hours > 0);
    closingTime = closingTime.add(_hours.mul(3600)); // convert to seconds and add to closingTimea
    if ( paused ) 
      unpause();
  }

  /**
  * @dev Sets the wallet to forward ETH collected funds
  */
  function setWallet(address paramWallet) public onlyOwner {
    require(paramWallet != 0x0);
    wallet = paramWallet;
  }

  /**
  *  allows to approve the sale if goal in dollars reached, or other admin reasons
  */
  function approve() public onlyOwner {
    conclude();
  }

  /**
  * @dev Finalizes the crowdsale, mint and transfer all ramaining tokens to owner
  */
  function conclude() internal {

    if (token.totalSupply() < HuhulaToken(token).cap()) {
      uint tokens = HuhulaToken(token).cap().sub(token.totalSupply());
      if ( ! HuhulaToken(token).mint(owner, tokens) ) {
        revert();
      }
    }
    HuhulaToken(token).finishMinting();

    // take onwership over HuhuToken contract
    HuhulaToken(token).transferOwnership(owner);
    
  }

  event BuyBackRateChange(uint32 rate);
  event BuyBackTransfer(address indexed from, address indexed to, uint256 value);
  event ReturnBuyBack(address indexed from, address indexed to, uint256 value);

  function setBuyBackRate(uint32 paramRate) public onlyOwner {
    require(paramRate >= 1);
    buyBackRate = paramRate;
    emit BuyBackRateChange(buyBackRate);
  }

  /**
  * Accumulate some Ether on address of this contract to do buyback
  */
  function fundForBuyBack() payable public onlyOwner returns(bool success) {
    return true;
  }
  
  /**
  * during buyBack tokens returned from given address and corresponding USD converted to ETH transferred back to holder
  */
  function buyBack(address _tokenHolder, uint256 _tokens) public onlyOwner {
    HuhulaToken(token).huhulaReturnToOwner(_tokenHolder, _tokens);
    uint256 buyBackWei = _tokens.mul(buyBackRate).mul(10**6);
    if ( _tokenHolder.send(buyBackWei) ) {
      emit BuyBackTransfer(address(this), _tokenHolder, buyBackWei);
    } else {
      revert();
    }
  }
 
  /**
  * during buyBack return funds from smart contract account to funds account
  */
  function returnBuyBackFunds() public onlyOwner {
    uint256 weiToReturn = address(this).balance;
    if ( wallet.send(weiToReturn) ) {
      emit ReturnBuyBack(this, wallet, weiToReturn);
    } else {
      revert();
    }
  }
 
}
