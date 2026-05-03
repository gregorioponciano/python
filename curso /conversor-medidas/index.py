#              km hm dam m dm cm mm

medida = float(input('Uma distância em metros: '))

km  = medida / 1000  # quilômetros
hm  = medida / 100   # hectômetros
dam = medida / 10    # decâmetros
dm  = medida * 10    # decímetros
cm  = medida * 100   # centímetros
mm  = medida * 1000  # milímetros

print('A medida de {}m corresponde a: \n{}km \n{}hm \n{}dam \n{:.0f}dm \n{:.0f}cm \n{:.0f}mm'.format(medida, km, hm, dam, dm, cm, mm))
