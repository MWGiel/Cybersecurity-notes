## HTB – SQL Basics: Finding Department Information in the employees Database
**Objective:**
Retrieve the department number (dept_no) for the department named "Development" from the MySQL/MariaDB employees database.

---
**1. List all databases**
> SHOW DATABASES
> employees

---
**2. Select the target database**
> USE employees

---
**3. List all tables in the database**
> SHOW TABLES

---
**Inspect the departments table structure**
> DESCRIBE departments

---
**5. Query the department number for "Development"**
> SELECT * FROM departments WHERE dept_name = 'Development'

---
## Answer
> Department number: d005

## Handling SQLMap Errors
- Display Errors
> The first step is usually to switch the --parse-errors, to parse the DBMS errors (if any) and displays them as part of the program run
## Store the Traffic
- The -t option stores the whole traffic content to an output file
> sqlmap -u "http://www.target.com/vuln.php?id=1" --batch -t /tmp/traffic.txt
## Verbose Output
- Another useful flag is the -v option, which raises the verbosity level of the console output:
> sqlmap -u "http://www.target.com/vuln.php?id=1" -v 6 --batch
## Using Proxy
- Finally, we can utilize the --proxy option to redirect the whole traffic through a (MiTM) proxy (e.g., Burp). This will route all SQLMap traffic through Burp, so that we can later manually investigate all requests, repeat them, and utilize all features of Burp with these requests
