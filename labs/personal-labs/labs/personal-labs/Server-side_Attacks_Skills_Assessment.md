## Today I did a lab on server side attacks, this is his wrietup
- First, I went to the website and used Burp Suite to intercept the requests and review them one by one.
- I entered the source code of the website and saw something like this: xhr.send'api=http://truckapi.htb/?id'encodeURIComponent("=" + truckID
- so I checked and saw that when entering the website there is a POST request with the value 'api='
- I tried to enter 127.0.0.1 instead of truckapi.htb but it didn't connect, but this information was enough for me
- I scan the ports on which the machine is running
- 80 and 3306 (sql port)
- ffuf -w /usr/share/seclists/Discovery/Web-Content/directory-list-lowercase-2.3-small.txt -u http://83.136.253.132:57554 -X POST -H "Content-Type: application/x-www-form-urlencoded" -d "api=http://truckapi.htb/FUZZ.php"
