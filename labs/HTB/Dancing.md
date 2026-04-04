#### Task1: What does the 3-letter acronym SMB stand for?
In networking and IT, the 3-letter acronym
SMB stands for Server Message Block.
#### Task 2: What port does SMB use to operate at?
The primary port for modern Server Message Block (SMB) communication is TCP port 445.
#### Task 3: What is the service name for port 445 that came up in our Nmap scan?
```html
nmap 10.129.60.214 -A
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-04-04 16:31 CDT
Nmap scan report for 10.129.60.214
Host is up (0.0080s latency).
Not shown: 997 closed tcp ports (reset)
PORT    STATE SERVICE       VERSION
135/tcp open  msrpc         Microsoft Windows RPC
139/tcp open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp open  *microsoft-ds*?
```
