largura = float(input('Largura da parede '))
altura = float(input('altura da parede '))

parede = largura * altura

print('a parede tem a dimensão de {} x {} e sua parede tem {}m²'.format(largura, altura, parede))

tinta = parede / 2

print('para pintar essa parede, você vai precisará de {}litros de tinta.'.format(tinta))
