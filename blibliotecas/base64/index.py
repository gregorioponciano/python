import base64

texto = "Acesso Autorizado"

# Codificando o texto para Base64
texto_codificado = base64.b64encode(texto.encode())
print(f"Codificado: {texto_codificado}")

# Decodificando de volta para o original
texto_original = base64.b64decode(texto_codificado).decode()
print(f"Decodificado: {texto_original}")