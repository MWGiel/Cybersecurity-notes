import socket 

def get_banner(sock):
    pass


def scan_port(target_ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            try:
                service = socket.getservbyport(port, 'tcp')
            except:
                service = 'Unknown'
            banner = get_banner(sock)
