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

#### Task 2: What software is running the service listening on the http/web port identified in the first question?
Command:
```html
nmap -sV -sC -A 10.129.97.64
```
Output:
```html
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 48:ad:d5:b8:3a:9f:bc:be:f7:e8:20:1e:f6:bf:de:ae (RSA)
|   256 b7:89:6c:0b:20:ed:49:b2:c1:86:7c:29:92:74:1c:1f (ECDSA)
|_  256 18:cd:9d:08:a6:21:a8:b8:b6:f7:9f:8d:40:51:54:fb (ED25519)
80/tcp open  http    Node.js (Express middleware)
|_http-title:  Bike 
```
Answer: **Node.js**

#### Task 3: What is the name of the Web Framework according to Wappalyzer?
<img width="257" height="311" alt="image" src="https://github.com/user-attachments/assets/fcb3b69a-dab0-4b37-bd52-878843a7609e" />

Answer: **Express**

#### Task 4: What software is running the service listening on the http/web port identified in the first question?
Command:
```html
nmap -sV -sC -A 10.129.97.64
```
Output:
```html
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 48:ad:d5:b8:3a:9f:bc:be:f7:e8:20:1e:f6:bf:de:ae (RSA)
|   256 b7:89:6c:0b:20:ed:49:b2:c1:86:7c:29:92:74:1c:1f (ECDSA)
|_  256 18:cd:9d:08:a6:21:a8:b8:b6:f7:9f:8d:40:51:54:fb (ED25519)
80/tcp open  http    Node.js (Express middleware)
|_http-title:  Bike 
```
Answer: **Node.js**

#### Task 5: What is the name of the vulnerability we test for by submitting {{7*7}}?

Answer: **Server Side Template Injection**

#### Task 6: What is the templating engine being used within Node.JS?
after pasting {{7*7}} into the e-mail field, the page returns an error:
```html
"{{7*7}}"
2	"--^"
3	"Expecting 'ID', 'STRING', 'NUMBER', 'BOOLEAN', 'UNDEFINED', 'NULL', 'DATA', got 'INVALID'"
4	"    at Parser.parseError (/root/Backend/node_modules/handlebars/dist/cjs/handlebars/compiler/parser.js:2
```
from this error you can read what engine is running on the web application
Answer: **handlebars**

