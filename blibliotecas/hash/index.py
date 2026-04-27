import hashlib

# O texto que queremos proteger (a senha do usuário)
senha = "minha_senha_segura"

# Criando um hash usando o algoritmo SHA-256 (um dos mais seguros)
hash_objeto = hashlib.sha256(senha.encode())
senha_criptografada = hash_objeto.hexdigest()

print(f"Senha original: {senha}")
print(f"Hash (Impressão digital): {senha_criptografada}")
# Mesmo que alguém veja o hash, não saberá qual é a senha original!