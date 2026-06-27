contract code:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Force { /*
                   MEOW ?
         /\_/\   /
    ____/ o o \
    /~____  =ø= /
    (______)__m_m)
                   */ }
```
**Vulnerability:** The contract is vulnerable to a forced ether injection via the selfdestruct opcode. In Solidity, contracts can reject normal Ether transfers by omitting the receive() and fallback() functions. However,
the Ethereum Virtual Machine (EVM) has system-level behaviors that bypass a contract's logic entirely. If another contract triggers a selfdestruct(target_address) instruction,
the remaining Ether of the destroying
contract is forcefully transferred to the target_address, regardless of whether the target contract wants it or has code to accept it.The core vulnerability lies within the total reliance on the contract's empty state as a security mechanism.
Because the contract cannot programmatically block a selfdestruct state update, an attacker can manipulate address(this).balance from the outside.

#### Exploit Steps

1. Deploy an Attacker Contract: Write and deploy a helper smart contract containing a payable function (or constructor) and the selfdestruct instruction.
```solidity
// SPDX-License-Identifier: MIT
pragma solidity >=0.6.12 <0.9.0;

contract Forceattacker {
    // Spacja przed nawiasami jest kluczowa dla kompilatora
    constructor() payable {
        // Pusty konstruktor, który pozwala na wpłatę ETH przy deployu
    }

    function attack(address payable target) public payable {
        selfdestruct(target);
    }
}
```
2. Fund the Attacker: When deploying the ForceAttacker contract (or when calling its attack function), ensure you send a small amount of Ether (e.g., 1 Wei or more) via your wallet (MetaMask) so its balance is greater than zero.
3. Execute the Attack: Call the attack function, passing your specific Ethernaut Instance address as the target parameter.
4. Verify the Balance: Confirm the attack was successful by checking the instance balance via the Ethernaut browser console. It will now show a value greater than zero, allowing you to complete the level.
