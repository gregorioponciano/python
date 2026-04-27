import secrets
import base64

# 1. Geramos uma chave de segurança ultra forte de 32 caracteres
# O modulo 'secrets' é seguro contra ataques de previsão
chave_secreta = secrets.token_hex(32) 
print(f"1. Chave gerada pelo sistema: {chave_secreta}")

# 2. Vamos 'ofuscar' (disfarçar) a chave usando Base64
# Isso é muito usado para enviar dados binários ou chaves em textos
chave_bytes = chave_secreta.encode('utf-8')
chave_codificada = base64.b64encode(chave_bytes)

print(f"2. Chave disfarçada (Base64) para envio: {chave_codificada.decode()}")

# 3. O destinatário recebe e transforma de volta no original
chave_decodificada = base64.b64decode(chave_codificada).decode('utf-8')
print(f"3. Chave recuperada no destino: {chave_decodificada}")