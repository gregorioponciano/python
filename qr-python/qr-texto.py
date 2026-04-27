# ========================================================================
# GERADOR DE QR CODE - VERSÃO FINAL DETALHADA
# ========================================================================
# Importamos a biblioteca principal. 
# Importante: Se der erro de 'PIL', rode 'pip install Pillow' no terminal.
import qrcode 

# --- PASSO 1: DEFINIR O CONTEÚDO ---
# Aqui dentro das aspas você pode colocar QUALQUER COISA:
# Pode ser um link: "https://google.com"
# Ou pode ser um texto simples: "Olá! Este é um teste de QR Code."
conteudo = "Olá! Este texto aparecerá quando você escanear o QR Code."

# --- PASSO 2: CRIAR O QR CODE ---
# O comando '.make()' transforma o seu texto em um padrão de blocos pretos e brancos.
# Ele cria um objeto de imagem na memória do computador.
imagem_qr = qrcode.make(conteudo)

# --- PASSO 3: SALVAR O ARQUIVO ---
# O comando '.save()' pega a imagem da memória e cria um arquivo físico.
# IMPORTANTE: Use sempre a extensão '.png' para ser reconhecido como imagem.
# O nome entre aspas é o nome que o arquivo terá na sua pasta à esquerda.
nome_do_arquivo = "meu_qrcode_teste.png"

try:
    # Tentamos salvar a imagem agora
    imagem_qr.save(nome_do_arquivo)
    
    # Se chegar aqui, imprimimos uma mensagem de sucesso no terminal
    print("--------------------------------------------------")
    print(f"✅ SUCESSO! QR Code gerado com o texto: '{conteudo}'")
    print(f"📂 Arquivo salvo como: {nome_do_arquivo}")
    print("--------------------------------------------------")

except Exception as erro:
    # Caso falte alguma biblioteca ou permissão, o Python avisa aqui:
    print(f"❌ ERRO AO SALVAR: {erro}")
    print("DICA: Verifique se você instalou o Pillow com 'pip install Pillow'")

# ========================================================================
# PARA EXECUTAR: No terminal, digite: python script.py
# ========================================================================
