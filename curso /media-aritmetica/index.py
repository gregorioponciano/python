n1 = float(input('Digite um numero '))
n2 = float(input('Digite o segundo numero '))

media = (n1 + n2) /2  #  primeira o ordem de precencia o parentes primeiro ()

        # :.1f (um ponto flutuante depois da virgula arredonda para cima 
        # ex: 5.5 + 2 = 3.75 mais fica 3.8 com :.1f)
print('A média entre {:.1f} e {:.1f} é igual a {:.1f}'.format(n1, n2, media))