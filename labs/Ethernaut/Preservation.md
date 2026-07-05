contract code:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Preservation {

  // public library contracts 
  address public timeZone1Library;
  address public timeZone2Library;
  address public owner; 
  uint storedTime;
  // Sets the function signature for delegatecall
  bytes4 constant setTimeSignature = bytes4(keccak256("setTime(uint256)"));

  constructor(address _timeZone1LibraryAddress, address _timeZone2LibraryAddress) {
    timeZone1Library = _timeZone1LibraryAddress; 
    timeZone2Library = _timeZone2LibraryAddress; 
    owner = msg.sender;
  }
 
  // set the time for timezone 1
  function setFirstTime(uint _timeStamp) public {
    timeZone1Library.delegatecall(abi.encodePacked(setTimeSignature, _timeStamp));
  }

  // set the time for timezone 2
  function setSecondTime(uint _timeStamp) public {
    timeZone2Library.delegatecall(abi.encodePacked(setTimeSignature, _timeStamp));
  }
}

// Simple library contract to set the time
contract LibraryContract {

  // stores a timestamp 
  uint storedTime;  

  function setTime(uint _time) public {
    storedTime = _time;
  }
}
```
**Vulnerability:** `setFirstTime` and `setSecondTime` both use `delegatecall` to run `LibraryContract.setTime` in the storage context of `Preservation`. `delegatecall` executes the callee's code but reads/writes the caller's storage *by slot index*, completely ignoring the callee's own variable names or types - it only cares about slot position. `LibraryContract` declares a single variable `storedTime` at slot 0, so when its `setTime` runs via `delegatecall` it writes to whatever occupies slot 0 in `Preservation`. But `Preservation`'s actual slot layout is:
- Slot 0: `timeZone1Library`
- Slot 1: `timeZone2Library`
- Slot 2: `owner`
- Slot 3: `storedTime`

So the library's write to "its" `storedTime` (slot 0) actually clobbers `timeZone1Library` in `Preservation`. This is a two-stage attack: first corrupt `timeZone1Library` to point at an attacker-controlled contract, then trigger `setFirstTime` again so the delegatecall executes the attacker's code, which can now write directly to slot 2 (`owner`) since the attacker chooses what "storedTime" means at whatever slot they like.

## Exploit Steps
1. Deploy an attacker contract whose storage layout mirrors `Preservation`'s first three slots (`slot0`, `slot1`, `owner`) so that when it is `delegatecall`'d into `Preservation`, its `setTime` function writes straight into `Preservation`'s `owner` slot:
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract preservationBraker {
  address public slot0;
  address public slot1; 
  address public owner; 

  function setTime(uint256) public {
    owner = address(tx.origin);
  }
  
}
```
Note the deliberate slot alignment: `slot0` and `slot1` are dummy placeholders matching `Preservation`'s `timeZone1Library`/`timeZone2Library`, so that `owner` in this attacker contract lands on slot 2 - exactly where `Preservation.owner` lives. `setTime` ignores its argument entirely and instead sets `owner` to `tx.origin`, i.e. whichever EOA initiated the top-level transaction.

2. Overwrite `timeZone1Library`: Call `setFirstTime(uint256(uint160(attackerContractAddress)))` on the `Preservation` instance. Because `LibraryContract.setTime` writes its single `uint` argument into slot 0 of the caller's storage, this delegatecall stores the attacker contract's address (cast to `uint256`) into `Preservation.timeZone1Library`.
3. Trigger the malicious library: Call `setFirstTime(anyValue)` on `Preservation` a second time. This time `timeZone1Library` points at `preservationBraker`, so the `delegatecall` executes *its* `setTime`, which writes `tx.origin` directly into slot 2 - `Preservation.owner` - regardless of the argument passed.
4. Verify the State: Confirm `owner()` on the `Preservation` instance now returns your EOA address, proving ownership was hijacked purely through storage-slot collision across two chained `delegatecall`s.
</content>
