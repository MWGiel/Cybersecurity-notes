## TCP (Transmission Control Protocol) and UDP (User Datagram Protocol)
are fundamental Transport Layer protocols in both OSI and TCP/IP models. They both handle application-to-application data transfer, yet they operate very differently when it comes to dependability, performance, and typical applications. Knowing how they differ is crucial for building fast and stable network systems.

### Transmission Control Protocol (TCP)
TCP is a dependable, connection-focused transport method that guarantees data arrives correctly and in sequence. It uses various checks and balances to ensure data integrity, which adds overhead but provides trustworthiness.

*Main points:*
Establishes a connection before sending data
Delivers data reliably and in proper order
More overhead, but very accurate

### User Datagram Protocol (UDP)
UDP is a speedy, connection-free transport method that fires off data without any delivery promises. It prioritizes efficiency for tasks where pace matters more than perfect accuracy.

*Main points:*
No connection setup, very lightweight
No assurance of arrival or sequence
Minimal overhead, very fast

Key Differences Between TCP and UDP

### TCP characteristics:
-    Requires a connection; sets it up via a three-way handshake
- Ensures dependable data transfer
- Relies on acknowledgement messages (ACKs)
- Resends any lost packets automatically
- Maintains correct packet sequence
- Manages transmission speed and network congestion
- More overhead means slower performance
- Header length can vary from 20 to 60 bytes
- Handles data as a smooth, continuous stream
- Cannot broadcast or multicast
- Common uses: HTTP, HTTPS, FTP, SMTP

### UDP characteristics:
- No connection needed; skips the handshake entirely
- Offers no delivery guarantee
- Does not use acknowledgements
- No built-in retransmission of dropped packets
- Packets may arrive in any order
- No speed or congestion management
- Very low overhead results in higher speed
- Header is always fixed at 8 bytes
- Treats each piece of data as a separate message
- Can broadcast and multicast
- Common uses: DNS, DHCP, VoIP, Streaming

