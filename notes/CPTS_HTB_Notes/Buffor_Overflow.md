1. RECONNAISSANCE     file, checksec, strings, nm, readelf
2. FIND THE BUG       objdump, source code, fuzzing
3. CHECK MITIGATIONS  NX? PIE? Canary? RELRO? ASLR?
4. FIND THE OFFSET    pattern + gdb + pwn cyclic
5. PICK A TECHNIQUE   ret2win / ret2libc / ROP / ret2dlresolve
6. BUILD THE PAYLOAD  pwntools
7. BYPASS ASLR        leak / brute-force / ret2plt
8. EXECUTE            locally → remote
9. MAINTAIN ACCESS    shell, persistence
10. REPORT            describe how to fix it

## Key Concepts

- What is EIP? — The instruction pointer (on 32-bit x86). It points to the next instruction the CPU will execute. Control EIP = control the program.

- What is the stack? — A region of memory that holds local variables and return addresses.

- What is SUID? — A permission bit that makes a program run with the privileges of the file's owner, not the user who launched it. SUID root = root.

- What is ASLR? — Address Space Layout Randomization. It randomizes memory addresses on every process start. It makes exploitation harder, but doesn't stop it.

- What is libc? — The C standard library loaded into every process. It contains system, execve, printf, etc. A primary target for exploitation.

- Why does ret2libc work? — Because system and /bin/sh are already in memory — you don't need to inject them yourself.
