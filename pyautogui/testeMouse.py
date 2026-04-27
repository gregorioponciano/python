import time      # Biblioteca para controlar o tempo
import pyautogui  # Biblioteca para capturar informações da tela e mouse

# 1. Dá uma pausa de 5 segundos antes de rodar o próximo comando.
# Esse tempo é para VOCÊ: serve para você tirar o mouse do terminal
# e colocá-lo exatamente em cima do botão ou campo que quer "mapear".
time.sleep(5) 

# 2. Captura a posição atual do cursor do mouse no exato momento 
# em que os 5 segundos acabarem e exibe no terminal.
# O resultado será algo como: Point(x=2718, y=262)
print(pyautogui.position()) 