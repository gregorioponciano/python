# --- INSTALAÇÃO (Executar no terminal com o venv ativo) ---
# pip install pyautogui  -> Biblioteca para controlar mouse, teclado e tela
# pip install pandas     -> Biblioteca para manipulação e análise de bases de dados
# pip install openpyxl   -> Necessário para o Pandas ler/escrever arquivos .xlsx (Excel)

import pyautogui  # Importa a ferramenta de automação de interface
import time       # Importa a ferramenta de controle de tempo/pausa
import pandas     # Importa a ferramenta de leitura de tabelas

# Configura uma pausa padrão de 2 segundos entre CADA comando do pyautogui
# Isso evita que o robô atropele o carregamento das janelas do Windows.
# pyautogui.PAUSE = 2

# --- COMANDOS DE TECLADO ---
# pyautogui.press('win')         # Pressiona a tecla Windows (Menu Iniciar)
# pyautogui.write('chrome')      # Digita o texto 'chrome' (cuidado com o nome correto)
# pyautogui.hotkey('win', 'r')   # Executa um atalho (Segura Windows e aperta R)

# --- COMANDOS DE MOUSE ---
# x e y são as coordenadas (pixels) da sua tela. 
# clicks=2 (clique duplo), button='right' (clique com botão direito).
# pyautogui.click(x=2569, y=354, clicks=2, button='right')

# --- AUXILIARES ---
# time.sleep(5)              # Pausa o código por 5 segundos (útil para abrir sites lentos)
# print(pyautogui.position()) # Exibe no terminal a posição exata (X, Y) onde seu mouse está agora

# --- INTEGRAÇÃO COM DADOS ---
# Lê o arquivo CSV e armazena toda a tabela na variável 'tabela'
# tabela = pandas.read_csv('produtos.csv') 
# print(tabela)               # Exibe a tabela no terminal para conferência

# --- ROLAGEM ---
# Controla o 'scroll' do mouse. Valores positivos sobem, negativos descem.
# pyautogui.scroll(10000) 
