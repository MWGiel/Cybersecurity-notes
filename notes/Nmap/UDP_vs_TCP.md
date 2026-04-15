# TCP vs UDP

## TCP (Transmission Control Protocol)
- **Connection:** Connection-oriented.
- **Mechanism:** Three-Way Handshake (SYN -> SYN-ACK -> ACK).
- **Reliability:** GUARANTEED.
  - Checks if packets arrived.
  - Retransmits lost packets.
  - Maintains packet order.
- **Speed:** Slower than UDP (overhead from acknowledgments).
- **Header Size:** 20-60 bytes.
- **Use Cases:** HTTP/HTTPS (web), SSH (port 22), FTP (port 21), SMTP (email).
- **HTB Scanning Relevance:** 
  - `-sT` (TCP Connect Scan) - completes full handshake.
  - `-sS` (SYN Stealth Scan) - half-open scan, default for `nmap` as root.

## UDP (User Datagram Protocol)
- **Connection:** Connectionless (Fire and Forget).
- **Mechanism:** Just sends datagrams. No handshake.
- **Reliability:** NOT GUARANTEED.
  - No guarantee of delivery.
  - No guarantee of order.
  - No duplicate protection.
- **Speed:** Faster. Lower latency.
- **Header Size:** 8 bytes (fixed).
- **Use Cases:** DNS (port 53), VoIP, Video Streaming, DHCP, SNMP, TFTP.
- **HTB Scanning Relevance:**
  - UDP scans are PAINFULLY SLOW.
  - Command: `nmap -sU <IP>`.
  - Often requires `--top-ports` to speed up.
  - If UDP port is open but service doesn't respond to empty probe, nmap shows `open|filtered`.

## TL;DR Analogy (for HTB enum mindset)
- **TCP:** Sending a package with tracking number and signature required. You know exactly if the server (target) received your SYN packet. Great for reliable shells and file transfers.
- **UDP:** Throwing a rock over a wall and hoping there's a bucket on the other side. You don't know if it landed unless someone yells back (ICMP Port Unreachable).

