import getpass

# Em vez de usar input(), usamos getpass()
# A senha não aparece enquanto você digita!
senha = getpass.getpass("Digite sua senha secreta: ")

if senha == "1234":
    print("Acesso liberado!")
else:
    print("Senha incorreta!")