# Ethernaut Magic Number Writeup

## Level Overview

**Objective:** Deploy a contract (called a "Solver") that:

1. Returns the number `42` when `whatIsTheMeaningOfLife()` is called on it.
2. Has a **runtime bytecode of at most 10 bytes**.

The level contract:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MagicNum {
    address public solver;

    constructor() {}

    function setSolver(address _solver) public {
        solver = _solver;
    }

    /*
    ____________/\\\_______/\\\\\\\\\_____        
     __________/\\\\\_____/\\\///////\\\___       
      ________/\\\/\\\____\///______\//\\\__      
       ______/\\\/\/\\\______________/\\\/___     
        ____/\\\/__\/\\\___________/\\\//_____    
         __/\\\\\\\\\\\\\\\\_____/\\\//________   
          _\///////////\\\//____/\\\/___________  
           ___________\/\\\_____/\\\\\\\\\\\\\\\_ 
            ___________\///_____\///////////////__
    */
}
```

The catch is the **10-byte limit** on the runtime code. Writing this in Solidity produces far more than 10 bytes (because Solidity injects a dispatcher, function selector checks, ABI decoding, etc.). So we have to write **raw EVM bytecode by hand**.

---

## Understanding the Constraint

When Ethernaut checks whether we solved the level, it does something like:

```solidity
MagicNum(instance).solver().whatIsTheMeaningOfLife()
```

If that call returns `42`, the level is solved.

The solver contract must **always return 42**, regardless of which function selector was used in the call. We don't even need to check the selector, we can just always return 42.

### What "10 bytes" actually means

When you deploy a contract, you send two pieces of bytecode:

1. **Creation code (init code)** — runs once during deployment. It's responsible for returning the **runtime code** that will be stored at the contract's address.
2. **Runtime code** — the code stored on-chain, executed on every call to the contract.

The `10 bytes` limit applies to the **runtime code**, not the creation code. The creation code can be longer.

---

## Designing the Runtime Code

Our runtime code needs to do two things:

1. Write the value `42` into memory.
2. Return 32 bytes from memory (starting at offset 0).

In EVM opcodes:

| Opcode | Hex | Description |
|--------|-----|-------------|
| `PUSH1 0x2a` | `60 2a` | Push `42` onto the stack |
| `PUSH1 0x00` | `60 00` | Push `0` (memory offset) onto the stack |
| `MSTORE` | `52` | Pop offset and value, write value to memory at offset |
| `PUSH1 0x20` | `60 20` | Push `32` (size to return) |
| `PUSH1 0x00` | `60 00` | Push `0` (memory offset to read from) |
| `RETURN` | `f3` | Pop offset and size, return that memory region |

Concatenated:

```
602a 6000 52 6020 6000 f3
```

That's **10 bytes**:

```
0x602a60005260206000f3
```

### Why `MSTORE` needs two stack arguments

`MSTORE` pops two values from the stack:

- **Top of stack** = memory offset (where to write)
- **Second value** = the 32-byte word to write

That's why we push `42` first (`PUSH1 0x2a`), then `0` (`PUSH1 0x00`). The value `0` ends up on top, and `MSTORE` uses it as the offset.

### Why `RETURN` needs two stack arguments

`RETURN` also pops two values:

- **Top of stack** = memory offset (where to start reading)
- **Second value** = number of bytes to return

We push `32` (`PUSH1 0x20`), then `0` (`PUSH1 0x00`). `RETURN` reads 32 bytes from memory starting at offset 0, which contains our stored `42` (padded to 32 bytes).

---

## Building the Creation Code

We need init code that returns the 10-byte runtime code above.

The init code must:

1. Store the runtime code somewhere in memory.
2. `RETURN` it to the EVM, so the EVM stores it as the new contract's code.

Standard pattern for init code:

```
PUSH1 <runtime_length>
PUSH1 <runtime_offset>
PUSH1 <memory_destination>
CODECOPY
PUSH1 <runtime_length>
PUSH1 <memory_destination>
RETURN
```

Let's lay it out.

We place the runtime code at memory offset `0x00` in the init code. Then:

- **Copy** runtime code from **calldata** (which contains the init code + runtime code) into memory.
- `CODECOPY` needs three arguments: destination offset, code offset, size.

Actually, let's use the simpler approach: `CODECOPY` (which copies from the **currently executing code**, i.e., the init code) — this is what the Solidity compiler does, and it's what we'll do.

### Layout

Let init code be:

```
[init prefix] [runtime code]
```

The `runtime code` starts at some offset `X` in the init code. We need:

```
PUSH1 0x0a        ; size = 10 bytes
PUSH1 0x0c        ; offset in code where runtime starts
PUSH1 0x00        ; memory destination
CODECOPY          ; mem[0..10] = code[0x0c..0x16]
PUSH1 0x0a        ; size = 10
PUSH1 0x00        ; memory offset
RETURN            ; return mem[0..10]
```

Let's check the sizes:

- `PUSH1 0x0a` → `600a` (2 bytes)
- `PUSH1 0x0c` → `600c` (2 bytes)
- `PUSH1 0x00` → `6000` (2 bytes)
- `CODECOPY` → `39` (1 byte)
- `PUSH1 0x0a` → `600a` (2 bytes)
- `PUSH1 0x00` → `6000` (2 bytes)
- `RETURN` → `f3` (1 byte)

Total init prefix = **12 bytes** (`0x0c` = 12). ✅ Matches the `0x0c` offset we used.

So the full creation code is:

```
600a600c600039600a6000f3   ← 12-byte init prefix
602a60005260206000f3       ← 10-byte runtime code
```

Concatenated:

```
0x600a600c600039600a6000f3602a60005260206000f3
```

That's **22 bytes** total creation code.

---

## Deployment via Console (web3.js)

```javascript
// 1. Define creation code
const bytecode = "0x600a600c600039600a6000f3602a60005260206000f3";

// 2. Deploy the solver contract
const tx = await web3.eth.sendTransaction({
    from: player,
    data: bytecode,
    gas: 100000
});

// 3. Wait for the receipt
await new Promise(r => setTimeout(r, 5000));
const receipt = await web3.eth.getTransactionReceipt(tx.transactionHash);
const solverAddress = receipt.contractAddress;

console.log("Solver deployed at:", solverAddress);

// 4. Verify runtime code
const code = await web3.eth.getCode(solverAddress);
console.log("Runtime code:", code);              // 0x602a60005260206000f3
console.log("Length:", (code.length - 2) / 2);  // 10

// 5. Verify return value
const answer = await web3.eth.call({ to: solverAddress, data: "0x" });
console.log("Answer:", answer);                 // 0x...002a

// 6. Register the solver with the MagicNum contract
await contract.setSolver(solverAddress);
```

If `contract.setSolver` is not available (as often happens in the Ethernaut console after a page refresh), encode the call manually:

```javascript
const selector = web3.utils.sha3("setSolver(address)").slice(0, 10); // 0x1f879433
const data = selector + "000000000000000000000000" + solverAddress.slice(2).toLowerCase();

await web3.eth.sendTransaction({
    from: player,
    to: instance,
    data: data,
    gas: 100000
});
```

---

## Deployment via Foundry

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "../src/MagicNum.sol";

contract MagicNumSolver is Script {
    function run() external {
        address instance = vm.envAddress("INSTANCE");

        vm.startBroadcast();

        // Deploy the minimal solver contract
        bytes memory creationCode = hex"600a600c600039600a6000f3602a60005260206000f3";
        address solver;
        assembly {
            solver := create(0, add(creationCode, 0x20), mload(creationCode))
        }

        // Register the solver
        MagicNum(instance).setSolver(solver);

        vm.stopBroadcast();
    }
}
```

---

## Verifying the Solution

After submitting the instance, Ethernaut runs:

```solidity
require(MagicNum(instance).solver().whatIsTheMeaningOfLife() == 42);
```

Let's trace it:

1. `solver()` returns the address we registered.
2. Calling `whatIsTheMeaningOfLife()` on that address sends a `CALL` with the function selector `0x5f5e5e0f` (or whatever it is — we don't check).
3. Our solver's runtime code **ignores** the selector entirely and always:
   - Writes `42` to memory.
   - Returns 32 bytes from memory.

So the caller receives `0x000000000000000000000000000000000000000000000000000000000000002a`, which the ABI decodes as `uint256(42)`. 

---

## Key Takeaways

### 1. EVM is a stack machine

Every opcode pops its arguments from the top of the stack. That's why argument order matters,  the value that needs to be on top must be pushed **last**.

### 2. Memory is a byte array

`MSTORE(offset, value)` writes 32 bytes to memory. `RETURN(offset, size)` reads `size` bytes from memory starting at `offset`.

### 3. Selector-based dispatch is a Solidity feature, not an EVM requirement

Solidity generates a dispatcher at the start of every contract to route calls by selector. But the EVM itself doesn't care — a contract can ignore selectors entirely (as we did here).

### 4. Creation code vs. runtime code

- **Creation code** runs once during `CREATE`/`CREATE2` and returns the runtime code.
- **Runtime code** is what's stored on-chain and executed on every call.
- The 10-byte limit applies to **runtime code**.

### 5. Hand-written bytecode can be dramatically smaller than compiler output

The Solidity equivalent of this contract would be **hundreds of bytes**. By writing raw EVM, we fit it into **10 bytes**. This is why some gas-optimized protocols use Yul or Huff.

---

## Full Bytecode Reference

### Runtime code (10 bytes)

```
0x602a60005260206000f3
```

| Bytes | Opcode | Meaning |
|-------|--------|---------|
| `60 2a` | `PUSH1 0x2a` | Push 42 |
| `60 00` | `PUSH1 0x00` | Push 0 |
| `52` | `MSTORE` | mem[0..32] = 42 |
| `60 20` | `PUSH1 0x20` | Push 32 |
| `60 00` | `PUSH1 0x00` | Push 0 |
| `f3` | `RETURN` | Return 32 bytes from mem[0] |

### Creation code (22 bytes)

```
0x600a600c600039600a6000f3602a60005260206000f3
```

| Bytes | Opcode | Meaning |
|-------|--------|---------|
| `60 0a` | `PUSH1 0x0a` | size = 10 |
| `60 0c` | `PUSH1 0x0c` | code offset = 12 |
| `60 00` | `PUSH1 0x00` | mem dest = 0 |
| `39` | `CODECOPY` | copy 10 bytes from code[12] to mem[0] |
| `60 0a` | `PUSH1 0x0a` | size = 10 |
| `60 00` | `PUSH1 0x00` | mem offset = 0 |
| `f3` | `RETURN` | return mem[0..10] |
| — | (runtime code) | `602a60005260206000f3` |

---

## Conclusion

The Magic Number level forces you to leave the comfort of Solidity and work directly with EVM bytecode. The solution is a 10-byte runtime contract that unconditionally returns 42. The creation code wraps that runtime code and returns it during deployment.

This exercise is a great introduction to:

- EVM opcode semantics (stack, memory, return).
- The difference between creation code and runtime code.
- Why hand-written bytecode matters for extreme gas/size optimization.
- How Solidity's ABI and selector dispatch is just a convention, not a requirement.

**Level cleared.** 
