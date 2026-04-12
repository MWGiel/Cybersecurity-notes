#### Task 1: What version of Apache is running on the target's port 80?
```html
80/tcp  open  http     Apache httpd 2.4.41 ((Win64) OpenSSL/1.1.1c PHP/7.2.28)
|_http-server-header: Apache/2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.2.28
```
Answer: **2.4.41**
#### Task 2: What username:password combination logs in successfully?
```html
ffuf -w /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt -X POST -d "username=admin&password=FUZZ" -H "Content-Type: application/x-www-form-urlencoded" -u http://10.129.25.141/ -H "Cookie: PHPSESSID=3chdskik276u1frrs362of9otv" -fc 401,403,404 -fs 66

:: Progress: [1/10000] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errorpassword                [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 29ms]
```
Answer: **admin:password**
#### Task 3: What is the word at the top of the page that accepts user input?
```html
<img width="898" height="516" alt="image" src="https://github.com/user-attachments/assets/e351d279-8071-462b-8b00-07f1a6429599" />

```
Answer: **Order**
#### Task 4: What XML version is used on the target?
Answer: **/etc/hosts/**
#### Task 5: Use a tool to brute force directories on the webserver. What is the full URL to the Magento login page?
```html
/admin
```
Answer: **/admin**
#### Task 6: Look up the password requirements for Magento and also try searching for the most common passwords of 2023. Which password provides access to the admin account?
After several attempts at common passwords and logging in, this is the password:
Answer: **qwerty123**
#### Task 7: Submit root flag
there was a flag on the dashboard after logging in
