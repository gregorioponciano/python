#  Celsius e Fahrenheit

c = float(input('Informe a temperatura em °C: '))

f = 9 * c / 5 +32
# f = ((9*c) / 5) +32 mesma ordem n precisa de parentes

print('A temperatura e de {}°Celsius corresponde a {}°Fahrenheit'.format(c, f))