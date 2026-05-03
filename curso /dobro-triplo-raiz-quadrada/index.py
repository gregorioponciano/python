n = int(input('Digite um numero \n'))

dobro = n*2
triplo = n*3
raiz = n** (1/2)    

print('O dobro de {} vale {}'.format(n, dobro))
print('O triplo de {} vale {}. \nA raiz quadrada de {} é igual a {:.2f}.'.format(n, triplo, n, raiz))

print('\n')
        # mesmo codigo de cima mais sem precisar das 3 variaveis
print('O dobro de {} vale {}'.format(n, (n*2)))
print('O triplo de {} vale {}. \nA raiz quadrada de {} é igual a {:.2f}.'.format(n, (n*3), n, pow(n, (1/2))))  # raiz quadrada poderia ser igual ao print acima o pow faz a mesma coisa(n**(1/2))

