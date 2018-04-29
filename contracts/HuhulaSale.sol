pragma solidity ^0.4.18;

import './HuhulaToken.sol';
import "zeppelin-solidity/contracts/math/SafeMath.sol";

import "zeppelin-solidity/contracts/ownership/Ownable.sol";
import "zeppelin-solidity/contracts/crowdsale/validation/TimedCrowdsale.sol";

/**
  Huhula crowdsale
*/
                                                                                     
contract HuhulaSale is Ownable, TimedCrowdsale(now + 1, now + 1 + HuhulaSale.SALE_DURATION) {
  using SafeMath for uint256;

//**********************************************************************************************
// ------------------------------ Customize Smart Contract ------------------------------------- 
//**********************************************************************************************
  uint256 constant _rate = 86304; // in USD cents per Ethereum
  address private constant _fundsWallet    = 0xa4aA1C90f02265d189a96207Be92597fFEaD54D2;
  string  public constant huhuTokenName = "Huhula Parking";
  string  public constant huhuTokenSymbol = "HUHU";
  uint256 public constant HUHULA_GOAL = 100000000000000000; // goal 100 tokens 
//**********************************************************************************************
  uint32 public buyBackRate = 1034; // in ETH with 6 decimal places per token, initially 0.001034
//**********************************************************************************************
  uint256 public constant SALE_DURATION = 5184000; 

  function HuhulaSale() public 
    Crowdsale(_rate, _fundsWallet, new HuhulaToken(huhuTokenName,huhuTokenSymbol) ) {
    require(_rate > 0);
    require(tokensGoal > 0);
    require(tokensGoal <= HuhulaToken(token).cap());
  }

  enum Statuses { SaleInProgress, PendingApproval, Disapproved, Succeeded }
  Statuses public status = Statuses.SaleInProgress;

  function setStatus(Statuses _status) internal {
    status = _status;
  }

  /**
   * @dev Modifier to make a function callable only when the contract is pendingApproval 
   */
  modifier whenPendingApproval() {
    require(status == Statuses.PendingApproval);
    _;
  }
  
  /**
   * @dev Modifier to make a function callable only when the contract is Approved
   */
  modifier whenSucceeded() {
    require(status == Statuses.Succeeded);
    _;
  }

  function calcTokens(uint256 weiAmount) internal constant returns(uint256) {
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
  event RateChange(uint256 rate);

  function mintTokens(address beneficiary, uint256 tokens) private returns(bool) {
    require(beneficiary != 0x0);
    require(tokens > 0);
//    require(now <= closingTime);                               // Crowdsale (without startTime check)

    if ( HuhulaToken(token).mint(beneficiary, tokens) ) {
      if ( HuhulaToken(token).approveSpender(beneficiary, owner, tokens) ) { // approve owner to return any token
        SpenderApproved(owner, tokens);
        return true;
      }
    }
    revert();      
    return false;
  }

  /**
  * @dev Sets SHACK to Ether rate. Will be called multiple times durign the crowdsale to adjsut the rate
  * since SHACK cost is fixed in USD, but USD/ETH rate is changing
  * @param paramRate defines SHK/ETH rate: 1 ETH = paramRate SHKs
  */
  function setRate(uint256 paramRate) public onlyOwner {
    require(paramRate >= 1);
    rate = paramRate;
    RateChange(paramRate);
  }

  // fallback function can be used to buy tokens
  function () external payable {
    buyTokens(msg.sender);
  }

  // low level token purchase function
  function buyTokens(address beneficiary) public payable {
    require(beneficiary != address(0));
    require(status == Statuses.SaleInProgress);
    require(now <= closingTime);                               // Crowdsale (without startTime check)
//    require(validPurchase());

    uint256 weiAmount = msg.value;
    // calculate token amount to be created
    uint256 tokens = calcTokens(weiAmount);

    // update state
    weiRaised = weiRaised.add(weiAmount);
    if ( mintTokens( beneficiary, tokens ) ) {
      TokenPurchase(address(0x0), beneficiary, weiAmount, tokens);
      forwardFunds();

      if ( token.totalSupply() >= tokensGoal ) {
        HuhulaToken(token).pause();
        setStatus(Statuses.PendingApproval);
      }
    }
        
  }

  // send ether to the fund collection wallet
  // override to create custom fund forwarding mechanisms
  function forwardFunds() internal {
    wallet.transfer(msg.value);
  }
  
  /**
  * @dev Allows to resume crowdsale if it was pending approval
  */
  function resume(uint256 _hours) public onlyOwner whenPendingApproval {
    require(_hours <= 744); // shorter than longest month, i.e. max one month
    require(_hours > 0);
    closingTime = closingTime.add(_hours.mul(3600)); // convert to seconds and add to closingTime

    setStatus(Statuses.SaleInProgress);
    if ( HuhulaToken(token).paused() ) {
      HuhulaToken(token).unpause();
    }
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
  function approve() public onlyOwner whenPendingApproval {
    setStatus(Statuses.Succeeded);
    conclude();
  }

  /**
  * allows to disapprove the sale if goal in dollars not reached, or other admin reasons
  */
  function disapprove() public onlyOwner whenPendingApproval {
    setStatus(Statuses.Disapproved);
    conclude();
  }
  
  /**
  * @dev Finalizes the crowdsale, mint and transfer all ramaining tokens to owner
  */
  function conclude() internal {

    if (token.totalSupply() < HuhulaToken(token).cap()) {
      uint tokens = HuhulaToken(token).cap().sub(token.totalSupply());
      if ( ! mintTokens(owner, tokens) ) {
        revert();
      }
    }
    HuhulaToken(token).finishMinting();

    // take onwership over ShacToken contract
    HuhulaToken(token).transferOwnership(owner);
    
  }

  event BuyBackRateChange(uint32 rate);
  event BuyBackTransfer(address indexed from, address indexed to, uint256 value);
  event ReturnBuyBack(address indexed from, address indexed to, uint256 value);

  function setBuyBackRate(uint32 paramRate) public onlyOwner {
    require(paramRate >= 1);
    buyBackRate = paramRate;
    BuyBackRateChange(buyBackRate);
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
    require(owner != _tokenHolder); // prevent buying back from borrower / token issuer
    if ( HuhulaToken(token).transferFrom(_tokenHolder, owner, _tokens) ) {
      uint256 buyBackWei = _tokens.mul(buyBackRate).mul(10**6);
      if ( _tokenHolder.send(buyBackWei) ) {
        BuyBackTransfer(this, _tokenHolder, buyBackWei);
      } else {
        revert();
      }
    }
  }

  /**
  * during buyBack return funds from smart contract account to funds account
  */
  function returnBuyBackFunds() public onlyOwner {
    uint256 weiToReturn = address(this).balance;
    if ( wallet.send(weiToReturn) ) {
      ReturnBuyBack(this, wallet, weiToReturn);
    } else {
      revert();
    }
  }
 
}
