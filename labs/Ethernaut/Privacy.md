contract code:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Privacy {
    bool public locked = true;
    uint256 public ID = block.timestamp;
    uint8 private flattening = 10;
    uint8 private denomination = 255;
    uint16 private awkwardness = uint16(block.timestamp);
    bytes32[3] private data;

    constructor(bytes32[3] memory _data) {
        data = _data;
    }

    function unlock(bytes16 _key) public {
        require(_key == bytes16(data[2]));
        locked = false;
    }
}
```
**Vulnerability:** The contract relies on the `private` visibility modifier to hide the unlock key, but `private` in Solidity only prevents *other contracts* from reading a variable through Solidity's own getter functions - it does **not** hide the data from the blockchain itself. All contract storage is publicly readable by anyone via `eth_getStorageAt`, regardless of visibility keywords. To exploit this, you must first work out *which storage slot* holds `data[2]`, since Solidity tightly packs consecutive state variables smaller than 32 bytes into shared slots to save gas:
- Slot 0: `locked` (bool, 1 byte)
- Slot 1: `ID` (uint256, 32 bytes - takes a full slot)
- Slot 2: `flattening` (uint8) + `denomination` (uint8) + `awkwardness` (uint16) packed together (4 bytes total, sharing one 32-byte slot)
- Slot 3: `data[0]`
- Slot 4: `data[1]`
- Slot 5: `data[2]` <- the key we need

Once `data[2]` is read from slot 5, the `unlock` function expects a `bytes16`, which is simply the first 16 bytes (the most significant bytes) of that `bytes32` value.

## Exploit Steps
1. Read storage slot 5 of the deployed instance directly from the chain:
```js
const slot5 = await web3.eth.getStorageAt(contractAddress, 5);
```
2. Truncate the value to its first 16 bytes (32 hex characters after `0x`) to obtain the `bytes16` key expected by `unlock`:
```js
const key = slot5.slice(0, 34); // "0x" + 32 hex chars
```
3. Call the `unlock` function passing the derived key:
```js
await contract.unlock(key);
```
4. Verify the State: Confirm that `locked` now returns `false`, proving the "private" data was successfully extracted straight from contract storage without ever needing the source-level access modifier to cooperate.
