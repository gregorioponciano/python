import requests

# 1. Vamos fazer uma requisição para o Google
url = "https://www.youtube.com"
resposta = requests.get(url)

# 2. Verificamos o 'Status Code' (200 significa que deu certo!)
print(f"Testando conexão com {url}...")
print(f"Status da resposta: {resposta.status_code}")

# 3. Verificamos qual tipo de servidor o site está usando
servidor = resposta.headers.get('Server')
print(f"O servidor alvo parece usar: {servidor}")