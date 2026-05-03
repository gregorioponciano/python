salario = float(input('Qual o o salario do funcionario? R$ '))

#  5 % de desconto
novo = salario + (salario * 15 / 100)

print('Seu salário é RS{:.2f}, e com 15% de aumento ficou R${:.2f}'.format(salario, novo))
