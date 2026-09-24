
# Ethernaut, Dex Writeup

## Level Overview

**Objective:** Drain one of the two tokens from the `Dex` contract. The level is solved when one of the token balances in the DEX reaches `0`.

**Victim contract:**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "openzeppelin-contracts-08/token/ERC20/IERC20.sol";
import "openzeppelin-contracts-08/token/ERC20/ERC20.sol";
import "openzeppelin-contracts-08/access/Ownable.sol";

contract Dex is Ownable {
    address public token1;
    address public token2;

    constructor() {}

    function setTokens(address _token1, address _token2) public onlyOwner {
        token1 = _token1;
        token2 = _token2;
    }

    function addLiquidity(address token_address, uint256 amount) public onlyOwner {
        IERC20(token_address).transferFrom(msg.sender, address(this), amount);
    }

    function swap(address from, address to, uint256 amount) public {
        require((from == token1 && to == token2) || (from == token2 && to == token1), "Invalid tokens");
        require(IERC20(from).balanceOf(msg.sender) >= amount, "Not enough to swap");
        uint256 swapAmount = getSwapPrice(from, to, amount);
        IERC20(from).transferFrom(msg.sender, address(this), amount);
        IERC20(to).approve(address(this), swapAmount);
        IERC20(to).transferFrom(address(this), msg.sender, swapAmount);
    }

    function getSwapPrice(address from, address to, uint256 amount) public view returns (uint256) {
        return ((amount * IERC20(to).balanceOf(address(this))) / IERC20(from).balanceOf(address(this)));
    }

    function approve(address spender, uint256 amount) public {
        SwappableToken(token1).approve(msg.sender, spender, amount);
        SwappableToken(token2).approve(msg.sender, spender, amount);
    }

    function balanceOf(address token, address account) public view returns (uint256) {
        return IERC20(token).balanceOf(account);
    }
}

contract SwappableToken is ERC20 {
    address private _dex;

    constructor(address dexInstance, string memory name, string memory symbol, uint256 initialSupply)
        ERC20(name, symbol)
    {
        _mint(msg.sender, initialSupply);
        _dex = dexInstance;
    }

    function approve(address owner, address spender, uint256 amount) public {
        require(owner != _dex, "InvalidApprover");
        super._approve(owner, spender, amount);
    }
}
```

At first glance, the DEX looks fine, it uses a constant-product-style pricing formula and requires the caller to own the tokens they want to swap. But there are two critical design flaws:

1. **No fees**, every swap is free. In real AMMs (Uniswap, SushiSwap), a 0.3% fee discourages repeated swaps and prevents the pool from being drained.
2. **No limit on the number of swaps**, you can swap back and forth as many times as you want, and each swap skews the price further.

Together, these allow an attacker to drain one side of the pool entirely by performing a sequence of increasingly large swaps.

---

## The Bug: Free Swaps and Skewed Reserves

The pricing formula is:

```
amountOut = (amountIn * balanceTo) / (balanceFrom + amountIn)
```

Where:

- `amountIn` — the amount you send,
- `balanceFrom` — the DEX's balance of the token you send,
- `balanceTo` — the DEX's balance of the token you want,
- `amountOut` — the amount you receive.

**This formula is mathematically correct for an AMM without fees.** But without fees, there is **no cost** to skewing the price. And because integer division rounds **down**, the DEX consistently receives a tiny bit more than it should — but the attacker can still make a profit by repeatedly swapping in increasing amounts.

The key insight: **each swap moves the pool further from equilibrium**. After a swap of `10 token1 → token2`, the DEX has `110 token1 / 91 token2`. The next swap (of `token2 → token1`) gets a **better rate** than the first one did, because the pool is already skewed. By alternating directions and increasing amounts, the attacker can drain the pool entirely.

---

## Starting State

- DEX: `100 token1`, `100 token2`
- Player: `10 token1`, `10 token2`

---

## The Exploit, Sequence of Swaps

The standard exploit sequence for this level is:

| Step | Swap | DEX (t1/t2) | Player (t1/t2) |
|------|------|-------------|-----------------|
| 0 | — | 100 / 100 | 10 / 10 |
| 1 | 10 t1 → t2 | 110 / 91 | 0 / 19 |
| 2 | 20 t2 → t1 | 91 / 110 | 20 / 0 |
| 3 | 24 t1 → t2 | 115 / 87 | 0 / 24 |
| 4 | 30 t2 → t1 | 86 / 116 | 30 / 0 |
| 5 | 41 t1 → t2 | 127 / 76 | 0 / 41 |
| 6 | 45 t2 → t1 | 82 / 120 | 45 / 0 |
| ... | continue until one side hits 0 | | |

After several iterations, one of the DEX's balances hits `0`, and the level is solved.

### Why this works

- **No fees** → each swap is free, so there's no cost to skewing the price.
- **No swap limit** → you can swap as many times as you want.
- **No arbitrage** → the DEX cannot rebalance itself (unlike real AMMs, where arbitrageurs restore equilibrium).
- **Integer rounding** → slightly favors the DEX each swap, but the attacker compensates by swapping **increasing amounts**.

---

## Executing the Attack

### 1. Approve the DEX to spend your tokens

In the Ethernaut console:

```javascript
await contract.approve(contract.address, 100)
```

Without this, `swap` will revert because `transferFrom` needs an allowance.

### 2. Perform the swaps

Each swap must be executed separately and confirmed before the next one:

```javascript
await contract.swap(token1, token2, 10)
await contract.swap(token2, token1, 20)
await contract.swap(token1, token2, 24)
await contract.swap(token2, token1, 30)
await contract.swap(token1, token2, 41)
await contract.swap(token2, token1, 45)
```

Where `token1` and `token2` are the addresses returned by `await contract.token1()` and `await contract.token2()`.

### 3. Verify the level is solved

```javascript
await contract.balanceOf(token1, contract.address)
await contract.balanceOf(token2, contract.address)
```

If either is `0`, the level is complete. Ethernaut will detect it automatically.

---

## Why This Is a Real-World Issue

The `Dex` contract is a simplified AMM **without fees**. In production AMMs like Uniswap V2, the formula includes a 0.3% fee:

```
amountOut = (amountIn * 997 * balanceTo) / (balanceFrom * 1000 + amountIn * 997)
```

The `997/1000` factor means every swap leaves 0.3% of the value in the pool. Over a sequence of swaps, the fees **compound** and make draining the pool unprofitable. Removing fees — as this challenge does — removes that protection.

This is a classic example of a **design flaw**, not a math flaw. The constant-product formula is correct; it's the **absence of fees** and the **absence of swap limits** that make it exploitable.

---

## Notes on `approve`

The `Dex.approve` function is a red herring for exploit purposes:

```solidity
function approve(address spender, uint amount) public {
    SwappableToken(token1).approve(msg.sender, spender, amount);
    SwappableToken(token2).approve(msg.sender, spender, amount);
}
```

- It has **no `onlyOwner`** — anyone can call it.
- It passes `msg.sender` as the `owner` in `SwappableToken.approve`.

But `SwappableToken.approve` has:

```solidity
require(owner != _dex, "InvalidApprover");
```

This blocks the DEX from approving its **own** tokens. So `Dex.approve` only lets the caller approve **their own** tokens — which is exactly what's needed for `swap` to work. It is **not** an exploit vector by itself; it's a poorly designed helper function.
