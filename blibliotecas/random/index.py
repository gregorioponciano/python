import random

# Gera um número inteiro aleatório entre 1 e 100
numero_sorteado = random.randint(1, 100)
print(f"O número da sua sorte hoje é: {numero_sorteado}")

# Escolhe uma opção aleatória de uma lista
opcoes = ["Maçã", "Banana", "Laranja"]
escolha = random.choice(opcoes)
print(f"A fruta escolhida foi: {escolha}")