## FireFlow machine writeup
<img width="877" height="540" alt="image" src="https://github.com/user-attachments/assets/9b4078f0-9e4a-4185-8122-2dc4d2c0c0b3" />

### 1. Reconnaissance

The target exposes three services: SSH on port 22, and Nginx on ports 80 and 443. The HTTPS site redirects to fireflow.htb, and further inspection reveals a virtual host flow.fireflow.htb hosting a Langflow instance. A playground page with an exposed flow_id indicates an unauthenticated endpoint that could be exploited.
### 2. Foothold

The Langflow installation is vulnerable to CVE-2026-33017, an unauthenticated remote code execution flaw that requires a valid flow_id. By crafting a request that injects a malicious Python component (a reverse shell), the attacker obtains a shell as www-data on the host system.
### 3. Privilege Escalation to nightfall

While exploring the filesystem, the attacker discovers Langflow’s environment file (.env) containing the password n1ghtm4r3_b4_n1ghtf4ll. This password is reused by the local user nightfall, who can now be accessed via SSH. The attacker retrieves the user flag from /home/nightfall/user.txt.
### 4. Lateral Movement to the MCP Pod

Inside nightfall’s home directory, a hidden .mcp folder holds a config.json file. It reveals the internal address of a custom MCP (Model Context Protocol) server, along with low‑privileged credentials (langflow-bot / Langfl0w@mcp2026!).
The server’s version endpoint discloses that JWT authentication is used, and that the algorithm none is supported. By crafting a JWT with the header "alg":"none" and a payload containing "role":"admin", the attacker forges an admin token without any signature.
Using this admin token, the attacker registers a new “tool” on the MCP server. The tool’s code spawns a reverse shell. When the tool is invoked via the JSON‑RPC endpoint, the code executes inside the MCP container, granting the attacker a shell as the mcp user within a Kubernetes pod.
### 5. Kubernetes Cluster Exploitation

Inside the pod, standard Kubernetes service account credentials are available. The associated service account mcp-sa is granted the permission to get resources of type nodes/proxy. This powerful permission allows the API server to proxy requests directly to the kubelet.
The attacker enumerates pods through the kubelet directly on port 10250 and discovers a privileged pod named prometheus-prometheus-node-exporter-nmntq in the monitoring namespace. Its node-exporter container runs with elevated privileges and has the entire host filesystem mounted at /proc, /sys, and / (the root filesystem).
Using the kubelet’s WebSocket exec interface, the attacker executes commands inside that privileged container. Because the host root filesystem is mounted directly, the attacker can read the root flag from /root/root.txt, effectively achieving full compromise of the underlying node.

### Key Vulnerabilities & Techniques:

- CVE-2026-33017, Unauthenticated RCE via Langflow component injection.

- Credential Reuse, Password from .env file reused for SSH login.

- JWT “none” Algorithm, Forging unsigned admin tokens.

- Dynamic MCP Tool Registration, Arbitrary code execution through a malicious tool.

- Kubernetes RBAC Misconfiguration, nodes/proxy permission grants access to the kubelet.

- Privileged Pod with HostPath Mount, Container escapes to the host filesystem.

This chain moves from an external web application vulnerability to full node compromise in a Kubernetes environment.

