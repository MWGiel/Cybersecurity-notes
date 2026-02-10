So far in this module, we have been exploiting file inclusion vulnerabilities to disclose local files through various methods. From this section, we will start learning how we can use file inclusion vulnerabilities to execute code on the back-end servers and gain control over them.

We can use many methods to execute remote commands, each of which has a specific use case, as they depend on the back-end language/framework and the vulnerable function's capabilities. One easy and common method for gaining control over the back-end server is by enumerating user credentials and SSH keys, and then use those to login to the back-end server through SSH or any other remote session. For example, we may find the database password in a file like config.php, which may match a user's password in case they re-use the same password. Or we can check the .ssh directory in each user's home directory, and if the read privileges are not set properly, then we may be able to grab their private key (id_rsa) and use it to SSH into the system.

Other than such trivial methods, there are ways to achieve remote code execution directly through the vulnerable function without relying on data enumeration or local file privileges. In this section, we will start with remote code execution on PHP web applications.
## Remote Code Execution
With allow_url_include enabled, we can proceed with our data wrapper attack. As mentioned earlier, the data wrapper can be used to include external data, including PHP code. We can also pass it base64 encoded strings with text/plain;base64, and it has the ability to decode them and execute the PHP code.

So, our first step would be to base64 encode a basic PHP web shell, as follows:
> [!bash!]$ echo '<?php system($_GET["cmd"]); ?>' | base64
# Command for reading the flag in CTF challange
> curl -s -X POST --data '<?php system($_GET["cmd"]); ?>' "http://<IP>:<PORT>/index.php?language=php://input&cmd=cat%20/37809e2f8952f06139011994726d9ef1.txt"
## Remote File Inclusion (RFI)
