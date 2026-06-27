contract code:
```solidity
solidity// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Vault {
    bool public locked;
    bytes32 private password;

    constructor(bytes32 _password) {
        locked = true;
        password = _password;
    }

    function unlock(bytes32 _password) public {
        if (password == _password) {
            locked = false;
        }
    }
}
```
**Vulnerability:** The contract is vulnerable to information disclosure due to a misconception about data privacy on the blockchain. In Solidity, marking a state variable as private only restricts other smart contracts from reading or modifying it programmatically.
However, the Ethereum blockchain is entirely public, meaning all compiled bytecode and state variable storage can be inspected by anyone off-chain.
State variables are sequentially mapped into 32-byte storage areas called slots. An attacker can leverage low-level JSON-RPC methods to look up the exact physical memory slot where the password is kept, rendering the private access modifier useless for keeping secrets.

## Exploit Steps
1.Locate the Target Slot: Identify where the password variable is stored. Variables are packed sequentially:
- Slot 0: bool public locked
- Slot 1: bytes32 private password
2. Read the Private Storage: Open the Ethernaut developer console in your browser and execute the low-level JSON-RPC storage lookup for Slot 1:
```javascript
  await web3.eth.getStorageAt(instance, 1)
```
3. Execute the Unlock: Copy the returned 32-byte hexadecimal string (including the 0x prefix) and pass it directly as the argument to the unlock function via the console:
```javascript
await contract.unlock("your_passwrod_here")
```
4. Verify the State: Confirm that the vault has been successfully breached by checking the public locked state variable. It should now return false:
```javascript
await contract.locked()
```
