import socket

# Tentando descobrir o endereço IP de um site
host = "www.youtube.com"

try:
    ip = socket.gethostbyname(host)
    print(f"O IP do site {host} é: {ip}")
except socket.gaierror:
    print("Não foi possível encontrar o IP.")