#### Task 1: Which service version is found to be running on port 80?
```html
PORT   STATE SERVICE VERSION
80/tcp open  http    nginx 1.14.2
|_http-title: Did not follow redirect to http://ignition.htb/
|_http-server-header: nginx/1.14.2
```
Answer: **nginx 1.14.2**
#### Task 2: What is the 3-digit HTTP status code returned when you visit http://{machine IP}/?
Answer: **302**
#### Task 3: What is the virtual host name the webpage expects to be accessed by?
```html
We can’t connect to the server at ignition.htb.
```
Answer: **ignition.htb**
#### Task 4: What is the full path to the file on a Linux computer that holds a local list of domain name to IP address pairs?
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
