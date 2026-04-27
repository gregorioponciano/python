import secrets
import string

# Gerar uma senha aleatória segura com 12 caracteres
alfabeto = string.ascii_letters + string.digits + string.punctuation
senha_forte = ''.join(secrets.choice(alfabeto) for i in range(12))

print(f"Sua nova senha ultra segura é: {senha_forte}")

# Gerar um link de "Recuperação de Senha" seguro
token_url = secrets.token_urlsafe(16)
print(f"URL de recuperação: https://meubanco.com/reset={token_url}")