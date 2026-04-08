#### Task 1: What TCP ports does nmap identify as open? Answer with a list of ports seperated by commas with no spaces, from low to high.
Command:
```html
nmap -sC 10.129.97.64
```
Output:
```html
PORT   STATE SERVICE
22/tcp open  ssh
| ssh-hostkey: 
|   3072 48:ad:d5:b8:3a:9f:bc:be:f7:e8:20:1e:f6:bf:de:ae (RSA)
|   256 b7:89:6c:0b:20:ed:49:b2:c1:86:7c:29:92:74:1c:1f (ECDSA)
|_  256 18:cd:9d:08:a6:21:a8:b8:b6:f7:9f:8d:40:51:54:fb (ED25519)
80/tcp open  http
|_http-title:  Bike 
```
Answer: **22**,**80**
