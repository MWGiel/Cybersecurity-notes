contract code :
```solidity
solidity// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

contract Token {
    mapping(address => uint256) balances;
    uint256 public totalSupply;

    constructor(uint256 _initialSupply) public {
        balances[msg.sender] = totalSupply = _initialSupply;
    }

    function transfer(address _to, uint256 _value) public returns (bool) {
        require(balances[msg.sender] - _value >= 0);
        balances[msg.sender] -= _value;
        balances[_to] += _value;
        return true;
    }

    function balanceOf(address _owner) public view returns (uint256 balance) {
        return balances[_owner];
    }
}
```
**Vulnerability:**
the contract is vulnerable to an integer underflow due to the lack of safe math checks in Solidity versions prior to 0.8.0. An attacker can pass a transfer amount greater than their actual balance, causing the balance calculation to wrap around to an extremely large number. The core vulnerability lies within the transfer() function's validation and subtraction logic:
```solidity
(balances[msg.sender] - _value >= 0);
```
balances[msg.sender] -= _value;
Since balances stores uint256 (unsigned integers), the result of the subtraction can never be negative. If _value is greater than balances[msg.sender], an underflow occurs, creating a massive positive number that bypasses the require check and inflates the attacker's balance.Exploit Steps
1. Determine your current token balance (the challenge provides you with exactly 20 tokens).
2. Call the transfer function from your player account via the Ethernaut console, sending more tokens than you currently own (e.g., 21 tokens) to any other valid Ethereum address:
```solidity
await contract.transfer("0x0000000000000000000000000000000000000000", 21);
```
3. Wait for the transaction to confirm. Your balance will underflow from 20 - 21, resulting in the maximum possible uint256 value, completing the level.
