## Router

A router forwards IP packets between different networks. It holds a routing table. For every packet, it reads the destination IP, finds the best route, and sends the packet out the right interface. Each interface sits in a different network, so the router is what stitches networks together. For hosts, the router is the default gateway.

A router decides at Layer 3, using IP addresses. It does not keep a MAC address table and does not forward frames like a switch. That single difference, IP packets versus Ethernet frames, is what separates a router from a switch.

The routing table is the heart of the device. Remove it and the router has no idea where to send anything.
## Layer 2 Switch vs Layer 3 Switch

A Layer 2 switch forwards Ethernet frames inside one network. It learns MAC addresses from every connected device and stores them in a MAC address table. When a frame arrives, the switch checks the destination MAC and sends the frame only out the port where that MAC lives. It works per VLAN. A pure Layer 2 switch cannot move traffic between VLANs because that requires routing, a Layer 3 job.

A Layer 3 switch does both. It switches frames at Layer 2 and routes IP packets between VLANs once you enable ip routing. It routes through an SVI or a routed physical port. In campus designs, the distribution switch is usually a Layer 3 switch.

- Layer 2 switch: forwards frames, uses MAC table, no routing between VLANs, sits at access layer

- Layer 3 switch: forwards frames and packets, uses MAC table plus routing table, routes between VLANs, needs ip routing command, sits at distribution layer

The MAC table on a Layer 2 switch shows dynamic entries, one MAC per port. There is no routing table. That contrast, routing table on a router versus MAC table on a switch, is the cleanest way to keep them apart.
## Next-Gen Firewalls and IPS

A firewall sits at the boundary between networks and decides what traffic passes. A traditional firewall looks at packet headers: source and destination IP, port, protocol. A next-generation firewall adds deep packet inspection, built-in IPS, application awareness, and threat intelligence feeds. It blocks on much more than just a port number.

IDS watches traffic and raises alerts but does not stop it. It sits off to the side. IPS sits inline in the traffic path and actively blocks what it detects. The whole difference is detect and warn versus detect and block.

- Packet filter: inspects IP, ports, protocol

- Stateful firewall: inspects headers plus connection state

- NGFW: inspects all of the above plus application, content, and threat intel

## Access Points: Autonomous vs Lightweight

An access point connects wireless clients to the wired network. Every AP sends and receives radio signals, but management logic lives in two very different places.

An autonomous AP is self-contained. It runs its own config, manages its own wireless network, needs its own management IP, and usually wants a trunk link. Ten autonomous APs means ten individual configs.

A lightweight AP handles only real-time radio work: sending frames, receiving frames, encrypting. Everything else, client association, roaming, authentication, security, QoS, is done centrally by a wireless LAN controller. This split is called split-MAC.

The SSID is the network name you see on your phone. The BSSID is the radio MAC of a specific AP serving that network. One SSID can come from many APs, each with its own BSSID.

- Autonomous AP: logic on the AP, config per AP, needs trunk link, keeps running alone

- Lightweight AP: logic on the WLC, central config, tunnels to WLC, depends on the controller

## Wireless LAN Controllers and CAPWAP

A WLC is the brain for a fleet of lightweight APs. It centralizes RF management, firmware, client assocRouter

A router forwards IP packets between different networks. It holds a routing table. For every packet, it reads the destination IP, finds the best route, and sends the packet out the right interface. Each interface sits in a different network, so the router is what stitches networks together. For hosts, the router is the default gateway.

A router decides at Layer 3, using IP addresses. It does not keep a MAC address table and does not forward frames like a switch. That single difference, IP packets versus Ethernet frames, is what separates a router from a switch.

The routing table is the heart of the device. Remove it and the router has no idea where to send anything.
Layer 2 Switch vs Layer 3 Switch

A Layer 2 switch forwards Ethernet frames inside one network. It learns MAC addresses from every connected device and stores them in a MAC address table. When a frame arrives, the switch checks the destination MAC and sends the frame only out the port where that MAC lives. It works per VLAN. A pure Layer 2 switch cannot move traffic between VLANs because that requires routing, a Layer 3 job.

A Layer 3 switch does both. It switches frames at Layer 2 and routes IP packets between VLANs once you enable ip routing. It routes through an SVI or a routed physical port. In campus designs, the distribution switch is usually a Layer 3 switch.

    Layer 2 switch: forwards frames, uses MAC table, no routing between VLANs, sits at access layer

    Layer 3 switch: forwards frames and packets, uses MAC table plus routing table, routes between VLANs, needs ip routing command, sits at distribution layer

The MAC table on a Layer 2 switch shows dynamic entries, one MAC per port. There is no routing table. That contrast, routing table on a router versus MAC table on a switch, is the cleanest way to keep them apart.
Next-Gen Firewalls and IPS

A firewall sits at the boundary between networks and decides what traffic passes. A traditional firewall looks at packet headers: source and destination IP, port, protocol. A next-generation firewall adds deep packet inspection, built-in IPS, application awareness, and threat intelligence feeds. It blocks on much more than just a port number.

IDS watches traffic and raises alerts but does not stop it. It sits off to the side. IPS sits inline in the traffic path and actively blocks what it detects. The whole difference is detect and warn versus detect and block.

    Packet filter: inspects IP, ports, protocol

    Stateful firewall: inspects headers plus connection state

    NGFW: inspects all of the above plus application, content, and threat intel

Access Points: Autonomous vs Lightweight

An access point connects wireless clients to the wired network. Every AP sends and receives radio signals, but management logic lives in two very different places.

An autonomous AP is self-contained. It runs its own config, manages its own wireless network, needs its own management IP, and usually wants a trunk link. Ten autonomous APs means ten individual configs.

A lightweight AP handles only real-time radio work: sending frames, receiving frames, encrypting. Everything else, client association, roaming, authentication, security, QoS, is done centrally by a wireless LAN controller. This split is called split-MAC.

The SSID is the network name you see on your phone. The BSSID is the radio MAC of a specific AP serving that network. One SSID can come from many APs, each with its own BSSID.

    Autonomous AP: logic on the AP, config per AP, needs trunk link, keeps running alone

    Lightweight AP: logic on the WLC, central config, tunnels to WLC, depends on the controller

Wireless LAN Controllers and CAPWAP

A WLC is the brain for a fleet of lightweight APs. It centralizes RF management, firmware, client association, roaming, security, and QoS. You manage wireless from one place.

The WLC and its APs talk over CAPWAP. This protocol builds two tunnels between each AP and the controller. The control channel runs on UDP 5246 and is always encrypted with DTLS. The data channel runs on UDP 5247 and can be encrypted optionally. Because traffic is tunneled, the AP and WLC do not need to be on the same subnet. You can drop a lightweight AP anywhere and it finds its controller.

Split-MAC also makes roaming smooth. When a client moves between APs, the controller already has the client state, so the handoff happens centrally.
Controllers and Centralized Management

A WLC is one type of controller, but the pattern is broader. A central controller programs and manages many devices instead of configuring each box by hand. It pushes config and policy, exposes REST APIs, and gives you one place to see and change the whole fabric. The intelligence moves off individual devices and into a controller, the same shift seen with lightweight APs and the WLC.
Endpoints and Servers

Endpoints generate and consume traffic: laptops, phones, tablets, cameras, IoT gadgets. They sit at the edge and have no forwarding role. Servers are specialized endpoints that provide shared services, DNS, DHCP, web, storage, authentication. They sit in the same conceptual spot as other endpoints but are typically rack-mounted, always on, and placed in their own data center segment.
Power over Ethernet

PoE lets a switch deliver power and data over one cable. An IP phone, AP, or camera needs only one wire. The switch port is the power sourcing equipment. The device drawing power is the powered device.

    802.3af (PoE): 15.4W from PSE, 12.95W at PD, 2 pairs, 2003

    802.3at (PoE+): 30W from PSE, 25.5W at PD, 2 pairs, 2009

    802.3bt (PoE++): up to 90W from PSE, up to 71.3W at PD, 4 pairs, 2018

IEEE standards negotiate before supplying power. Newer standards use LLDP to fine-tune wattage. Passive PoE is always on and can damage devices not built for it. The standards are backward compatible, an older phone plugged into a newer switch simply negotiates down.iation, roaming, security, and QoS. You manage wireless from one place.

The WLC and its APs talk over CAPWAP. This protocol builds two tunnels between each AP and the controller. The control channel runs on UDP 5246 and is always encrypted with DTLS. The data channel runs on UDP 5247 and can be encrypted optionally. Because traffic is tunneled, the AP and WLC do not need to be on the same subnet. You can drop a lightweight AP anywhere and it finds its controller.

Split-MAC also makes roaming smooth. When a client moves between APs, the controller already has the client state, so the handoff happens centrally.
## Controllers and Centralized Management

A WLC is one type of controller, but the pattern is broader. A central controller programs and manages many devices instead of configuring each box by hand. It pushes config and policy, exposes REST APIs, and gives you one place to see and change the whole fabric. The intelligence moves off individual devices and into a controller, the same shift seen with lightweight APs and the WLC.
## Endpoints and Servers

Endpoints generate and consume traffic: laptops, phones, tablets, cameras, IoT gadgets. They sit at the edge and have no forwarding role. Servers are specialized endpoints that provide shared services, DNS, DHCP, web, storage, authentication. They sit in the same conceptual spot as other endpoints but are typically rack-mounted, always on, and placed in their own data center segment.
## Power over Ethernet

PoE lets a switch deliver power and data over one cable. An IP phone, AP, or camera needs only one wire. The switch port is the power sourcing equipment. The device drawing power is the powered device.

- 802.3af (PoE): 15.4W from PSE, 12.95W at PD, 2 pairs, 2003

- 802.3at (PoE+): 30W from PSE, 25.5W at PD, 2 pairs, 2009

- 802.3bt (PoE++): up to 90W from PSE, up to 71.3W at PD, 4 pairs, 2018

IEEE standards negotiate before supplying power. Newer standards use LLDP to fine-tune wattage. Passive PoE is always on and can damage devices not built for it. The standards are backward compatible, an older phone plugged into a newer switch simply negotiates down.
