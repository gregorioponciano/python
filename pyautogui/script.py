import pyautogui
import time
import pandas

# 1. Carrega o banco de dados de produtos para a memória
tabela = pandas.read_csv('produtos.csv') 

# 2. Configura uma pausa de segurança de 0.5s entre cada comando do robô
# Isso ajuda o sistema a não "engasgar" com a velocidade dos comandos.
pyautogui.PAUSE = 0.5

# --- INÍCIO DA AUTOMAÇÃO (Abertura do Navegador) ---
pyautogui.press('win')         # Abre o Menu Iniciar
time.sleep(1)                  # Espera o menu carregar
pyautogui.write('chrome')      # Digita o nome do navegador
pyautogui.press('enter')       # Confirma a abertura
time.sleep(4)                  # Espera o navegador abrir completamente

# Digita a URL do sistema de destino e acessa
pyautogui.write('https://dlp.hashtagtreinamentos.com/python/intensivao/login')
pyautogui.press('enter')
time.sleep(4)                  # Aguarda o site carregar

# --- PROCESSO DE LOGIN ---
# Clica no campo de e-mail (Coordenada X, Y específica da sua tela)
pyautogui.click(x=2689, y=372)
pyautogui.write('gregorioponci.91@gmail.com')
pyautogui.press('tab')         # Pula para o campo de senha
pyautogui.write('12345678')
pyautogui.press('tab')         # Pula para o botão de login
pyautogui.press('enter')       # Efetua o login
time.sleep(3)                  # Espera carregar a página interna

# --- LOOP DE CADASTRO (Repetição para cada linha da tabela) ---
# tabela.index percorre cada linha (0, 1, 2...) do arquivo CSV
for linha in tabela.index: 
    # Clica no primeiro campo do formulário de cadastro
    pyautogui.click(x=2718, y=262)
    
    # Extrai o "codigo" da linha atual e digita no formulário
    codigo = tabela.loc[linha, "codigo"]
    pyautogui.write(str(codigo))   # str() garante que números sejam tratados como texto
    pyautogui.press('tab')
    
    # Extrai a "marca" e digita
    marca = tabela.loc[linha, "marca"]
    pyautogui.write(str(marca))
    pyautogui.press('tab')
    
    # Extrai o "tipo" e digita
    tipo = tabela.loc[linha, "tipo"]    
    pyautogui.write(str(tipo))
    pyautogui.press('tab')
    
    # Extrai a "categoria" e digita
    categoria = tabela.loc[linha, "categoria"]
    pyautogui.write(str(categoria))       
    pyautogui.press('tab')

    # Extrai o "preço_unitario" e digita
    preço_unitario = tabela.loc[linha, "preco_unitario"]
    pyautogui.write(str(preço_unitario))
    pyautogui.press('tab')

    # Extrai o "custo" e digita
    custo = tabela.loc[linha, "custo"]
    pyautogui.write(str(custo))
    pyautogui.press('tab')

    # Trata o campo "obs" (Observações)
    # No Pandas, campos vazios aparecem como "nan" (not a number)
    obs = str(tabela.loc[linha, "obs"])
    if obs != "nan":               # Só digita se o campo não estiver vazio
        pyautogui.write(obs)
    pyautogui.press('tab')

    # Finaliza o cadastro do produto atual
    pyautogui.press('enter')
    
    # Rola a página para cima para garantir que o formulário esteja visível para o próximo loop
    pyautogui.scroll(10000)
