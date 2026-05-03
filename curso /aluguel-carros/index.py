dias = int(input('Quantos dias alugados? '))
hm = float(input('Quantos Km rodados? '))
pago = dias * 60
print('O total a pagar é de R${:.2f}'.format(pago))