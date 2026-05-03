preço = float(input('Qual o preço do produto? R$ '))

#  5 % de desconto
novo = preço - (preço * 5 / 100)

print('O produto que custava R${}, na promoçao ele vai custar RS{}'.format(preço, novo))
