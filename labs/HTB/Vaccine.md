#### Task1: Besides SSH and HTTP, what other service is hosted on this box?
```html
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
```
Answer: **FTP**
#### Task 2: This service can be configured to allow login with any password for specific username. What is that username?
Answer: **Anonymous**
#### Task 3: What is the name of the file downloaded over this service?
```html
tp> ls
229 Entering Extended Passive Mode (|||10915|)
150 Here comes the directory listing.
-rwxr-xr-x    1 0        0            2533 Apr 13  2021 backup.zip
```
Answer: **backup.zip**
#### Task 4: What script comes with the John The Ripper toolset and generates a hash from a password protected zip archive in a format to allow for cracking attempts?

Answer: **zip2john**
#### Task 5: What is the password for the admin user on the website?
```html
ftp> get backup.zip
local: backup.zip remote: backup.zip
229 Entering Extended Passive Mode (|||10746|)
150 Opening BINARY mode data connection for backup.zip (2533 bytes).
100% |***********************************|  2533        1.08 MiB/s    00:00 ETA
226 Transfer complete.
```
```html
zip2john backup.zip > hash.txt
```
```html
smbclient -L 10.129.60.214 -N
```
```html
smbclient -L 10.129.60.214 -N
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
