import re

email = "contato@python.com"
padrao = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

if re.match(padrao, email):
    print("E-mail válido!")
else:
    print("Formato de e-mail inválido.")