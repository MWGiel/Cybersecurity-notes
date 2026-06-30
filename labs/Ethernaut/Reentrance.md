Contract code:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;

import "openzeppelin-contracts-06/math/SafeMath.sol";

contract Reentrance {
    using SafeMath for uint256;

    mapping(address => uint256) public balances;

    function donate(address _to) public payable {
        balances[_to] = balances[_to].add(msg.value);
    }

    function balanceOf(address _who) public view returns (uint256 balance) {
        return balances[_who];
    }

    function withdraw(uint256 _amount) public {
        if (balances[msg.sender] >= _amount) {
            (bool result,) = msg.sender.call{value: _amount}("");
            if (result) {
                _amount;
            }
            balances[msg.sender] -= _amount;
        }
    }

    receive() external payable {}
}
```


**Vulnerability:** The contract is vulnerable to a Reentrancy attack due to the violation of the checks-effects-interactions pattern. In Solidity, using .call{value: x}("") to send funds to an address executes the recipient's receive/fallback function before the state is updated. Because the contract updates the user's balance after sending the Ether, a malicious contract can recursively call the withdraw() function within its receive() handler, repeatedly draining funds from the contract. Each recursive call still sees the original balance since the state hasn't been updated yet, allowing the attacker to withdraw more than their actual deposited amount and potentially drain the entire contract balance.

## Exploit Steps

1. Deploy a custom smart contract capable of recursively calling the withdraw function whenever it receives Ether:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.12;

import "openzeppelin-contracts-06/math/SafeMath.sol";

contract Reentrance {
    using SafeMath for uint256;

    mapping(address => uint256) public balances;

    function donate(address _to) public payable {
        balances[_to] = balances[_to].add(msg.value);
    }

    function balanceOf(address _who) public view returns (uint256 balance) {
        return balances[_who];
    }

    function withdraw(uint256 _amount) public {
        if (balances[msg.sender] >= _amount) {
            (bool result,) = msg.sender.call{value: _amount}("");
            if (result) {
                _amount;
            }
            balances[msg.sender] -= _amount;
        }
    }

    receive() external payable {}
}
```

2. Fund and Initiate the Attack: Call the donate() function on your deployed contract, passing the Reentrance instance address and providing enough value (ether) to deposit into the target contract. Then call the attack() function to trigger the first withdrawal.

3. Induce Reentrancy Loop: When the target contract sends Ether to your attack contract, the receive() function is triggered. This function checks if the target still has funds and recursively calls withdraw() again. Since the target hasn't updated the attacker's balance yet, each recursive call succeeds, draining the contract's balance.

4. Verify the State: Confirm that the target contract's balance is reduced to zero and your attack contract holds all the stolen funds. Call withdrawFunds() to retrieve the drained Ether.


