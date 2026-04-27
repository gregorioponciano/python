from scapy.all import IP, ICMP, sr1

# 1. Vamos criar um pacote de 'Ping' (ICMP) do zero
# IP(dst=...) define o destino, ICMP() define o tipo de mensagem
pacote = IP(dst="8.8.8.8") / ICMP()

print("Enviando um pacote de rede customizado (Ping)...")

# 2. Envia o pacote e espera por 1 resposta (sr1 = send and receive 1)
resposta = sr1(pacote, timeout=2, verbose=0)

# 3. Verifica se o alvo respondeu
if resposta:
    print(f"Resposta recebida de: {resposta.src}")
    resposta.show() # Mostra todos os detalhes técnicos do pacote recebido
else:
    print("O alvo não respondeu ao pacote.")
