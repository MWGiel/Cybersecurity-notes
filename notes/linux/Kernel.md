# Linux Kernel – Concise Notes

## What is the Linux Kernel?
- Core component of the Linux operating system.
- Interface between hardware and user-space processes.
- Manages system resources: CPU, memory, devices, filesystems, I/O.

## Key Responsibilities
1. **Process Management** – scheduling, creation/termination, context switching.
2. **Memory Management** – virtual memory, paging, swapping, allocation.
3. **Device Management** – drivers, device trees, I/O handling.
4. **File System Management** – VFS (Virtual File System), actual filesystems (ext4, XFS, btrfs).
5. **Networking** – protocol stack (TCP/IP, UDP), routing, netfilter.
6. **Security** – permissions, capabilities, SELinux/AppArmor, namespaces.

## Architecture Overview
- **Monolithic kernel** – all core services in one binary, but with loadable modules.
- **Layered structure** (from inside out):
  - Hardware
  - Kernel core (scheduler, memory mgr, IPC, VFS)
  - System call interface (syscalls)
  - User space (applications, shells, libraries)

## Important Concepts

### Kernel Space vs User Space
- **Kernel space** – privileged mode, direct hardware access.
- **User space** – restricted, uses syscalls to request kernel services.

### System Calls (syscalls)
- Controlled entry points from user to kernel (e.g., `read`, `write`, `open`, `fork`).
- Defined in `unistd.h`.

### Modules
- `.ko` files – loadable kernel modules.
- Insert/remove at runtime: `insmod`, `rmmod`, `modprobe`.

### Interrupts & Exceptions
- **Interrupts** – hardware events (keyboard, disk, timer).
- **Exceptions** – software faults (page fault, division by zero).

### Scheduling
- Preemptive multi-tasking.
- Completely Fair Scheduler (CFS) – default since 2.6.23.
- Real-time scheduling options (FIFO, RR).

### Memory Management
- Virtual memory per process (via MMU).
- Pages (usually 4KB), page tables.
- **Swap** – moves inactive pages to disk.
- **OOM Killer** – kills processes when memory exhausted.

## Common Directories in `/proc` and `/sys`
- `/proc/cpuinfo` – CPU info.
- `/proc/meminfo` – memory stats.
- `/proc/modules` – loaded modules.
- `/sys/kernel/` – tunable kernel parameters.

## Versioning (example)
- `5.10.0` → major.minor.patch
- Even minor numbers used to indicate stable (older scheme), now more time-based.