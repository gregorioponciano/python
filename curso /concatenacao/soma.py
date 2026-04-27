n1 = int(input('digite um numero')); # int faz o numero de strig para number
n2 = int(input('digite um numero')); 
s = (n1 + n2); # adiciona + como string coloca um numero na frente do outro e nao soma 
print('a some vale' , s)

# Forma correta usando .format()
print('a some vale({})'.format(s))

# Forma moderna e recomendada (f-string)
print(f'a some vale({s})')

print(type(n1))

print('a soma entre {} e {} vale {}'.format(n1, n2, s))


# int 7 -4 0 9875 

#float 4.5 0.076 -15.223 numero real ou ponto flutuante

#bool True False # primeira letra maiuscula

#str 'ola' '7.5' '' tudo que estiver dentro as aspas 
