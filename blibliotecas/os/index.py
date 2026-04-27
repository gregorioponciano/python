import os

# 1. Vamos descobrir em qual pasta estamos agora
pasta_atual = os.getcwd()
print(f"Você está na pasta: {pasta_atual}")

# 2. Criar uma pasta nova para o nosso Banco
if not os.path.exists("meu_banco_dados"):
    os.mkdir("meu_banco_dados")
    print("Pasta 'meu_banco_dados' criada com sucesso!")
else:
    print("A pasta já existe.")