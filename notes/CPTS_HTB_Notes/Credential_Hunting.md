
# Credential Hunting



##### Objective
Find passwords, SSH keys, tokens, and other credentials on the system to gain access to other users, databases, or systems within the environment.



##### Where to Look

## 1. Configuration Files
+ .conf, .config, .xml, .ini, .json, .yaml, .yml
+ Commonly contain database passwords, API keys, and service credentials.

```bash
find / -iname "*config*" -type f 2/dev/null
```

## 2. Scripts (.sh, .py, .pl, .rb)
```bash
grep -r "password" /home*/ 2/dev/null
```
Contain passwords used for automation tasks.

## 3. Bash History
```bash
cat ~/.bash_history
```
Contains commands with passwords entered directly on the command line i.e. &quot;mysql -u root -pHaślo&quot;.

## 4. Temporary and Backup Files
+ .bak, .old, .tmp, .swp, ~
( These may contain copies of sensitive data.

## 5. Web Root (/var/www)
```bash
grep -r "password" /var/www/ 2/dev/null
```
EX. WordPress &quot;wp-config.php&quot; contains MYSQL credentials.

## 6. Mail Directories (/var/mail, /var/spool/mail)
Can contain emails with passwords or other sensitive information.



##### SSH Keys

## Locations
```bash
~/.ssh/
/home/*/.ssh/
```

## Files to Check

| File              | Purpose                                       |
|---------------|--------------------------------------------------|
 | `id_rsa`         | Private SSH key - can be used to log in as other users  |
 | `id_rsa.pub`     | Public SSH key                                   |
 | `known_hosts`    | List of hosts the user has connected to            |
 | `authorized_keys` | Keys allowed to log in as this user            |

## Once you find a private key, you can use it to connect:
```bash
ssh -i id_rsa user@host
```



##### Examples of Discovered Credentials

## WordPress (MySQL credentials)
```bash
grep 'DB_USER|DB_PASSWORD' wp-config.php
```

Example output:
```
define( 'DB_USER', 'wordpressuser' );
define( 'DB_PASSWORD', 'WPadmin123!' );
```

## Searching for credentials across the system
```bash
ghrep  -r "password" / 2/dev/null
```
