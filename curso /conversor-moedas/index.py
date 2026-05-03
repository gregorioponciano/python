real = float(input('Quanto dinheiro você tem na carteira? R$ '))
dolar = real / 4.95 # dia 03/05/26
print('Com R${:.2f}\nvocê pode comprar U${:.2f}'.format(real, dolar))