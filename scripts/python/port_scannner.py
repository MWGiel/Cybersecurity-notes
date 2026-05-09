import socket 
import concurrent.futures
import sys

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

def format_port_result(results):
    if not results:
        return "No open ports found."
    
    formatted_results = "Port Scan Results:\n"
    formatted_results += "{:<8} {:<15} {:<10}\n".format("Port", "Service", "Status")
    formatted_results += '-' * 35 + "\n"
    
    for port, service, banner, status in results:
        if status:  # tylko otwarte porty
            formatted_results += f"{RED}{port:<8} {service:<15} {'Open':<10}{RESET}\n"
            if banner and banner.strip():
                banner_lines = banner.split('\n')
                for line in banner_lines:
                    if line.strip():
                        formatted_results += f"{GREEN}{'':<8}{line.strip()}{RESET}\n"
    
    return formatted_results  # Poprawione - usunięto "rn formatted_results"

def get_banner(sock):
    try:
        sock.settimeout(1)
        banner = sock.recv(1024).decode().strip()
        return banner
    except:
        return " "

def scan_port(target_ip, port):
    sock = None
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
            return port, service, banner, True
        else:
            return port, "", "", False
    except Exception as e:
        return port, "", "", False
    finally:
        if sock:
            sock.close()

def port_scan(target_host, start_port, end_port):
    target_ip = socket.gethostbyname(target_host)
    print(f"Starting scan on host: {target_ip}")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=400) as executor:
        futures = {executor.submit(scan_port, target_ip, port): port for port in range(start_port, end_port + 1)}
        total_ports = end_port - start_port + 1
        for i, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            port, service, banner, status = future.result()
            results.append((port, service, banner, status))  # Poprawione: result -> results
            sys.stdout.write(f"\rProgress: {i}/{total_ports} ports scanned")  # Poprawione: dodano f-string
            sys.stdout.flush()

    sys.stdout.write("\n")
    print(format_port_result(results))  # Poprawione: format_port_results -> format_port_result

if __name__ == '__main__':
    target_host = input("Enter your target ip: ")
    start_port = int(input("Enter the start port: "))
    end_port = int(input("Enter end port: "))  # Poprawione: "and" -> "end"

    port_scan(target_host, start_port, end_port)
