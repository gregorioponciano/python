# ========================================================================
# GERADOR DE QR CODE CUSTOMIZADO - VERSÃO ULTRA DETALHADA
# ========================================================================
# Desenvolvido para criar QR Codes com cores personalizadas e alta precisão.
# Requisito: pip install qrcode[pil] Pillow
# ========================================================================

import qrcode  # Biblioteca base para codificação dos dados em matriz QR

def gerar_qr_code_colorido(conteudo, nome_arquivo):
    """
    Função para gerar QR Code com fundo/borda verde e módulos pretos.
    """
    try:
        # --- PASSO 1: CONFIGURAÇÃO ESTRUTURAL ---
        # Aqui definimos a "carcaça" do QR Code antes de colocar as cores.
        qr = qrcode.QRCode(
            version=1,  # Versão 1 é a matriz básica (21x21). Aumenta conforme o volume de dados.
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Nível Alto (H): Permite leitura mesmo se 30% do QR estiver danificado.
            box_size=10,  # Define que cada "pixel" do QR terá 10x10 pixels reais na imagem.
            border=4,     # Define a espessura da margem (padrão oficial da norma ISO é 4).
        )

        # --- PASSO 2: INSERÇÃO DE DADOS ---
        # O método add_data prepara o texto/link para ser convertido em binário.
        qr.add_data(conteudo)
        # O 'fit=True' força o QR Code a encontrar a menor versão possível para o texto inserido.
        qr.make(fit=True)

        # --- PASSO 3: ESTILIZAÇÃO DE CORES (MUDANÇA AQUI!) ---
        # fill_color: Define a cor dos "quadradinhos" (módulos). Mantivemos 'black'.
        # back_color: Define a cor do FUNDO e da BORDA. Alteramos para 'green'.
        # Você pode usar nomes ('green', 'red') ou códigos Hexadecimais ('#00FF00').
        imagem = qr.make_image(
            fill_color="black", 
            back_color="blue"
        )

        # --- PASSO 4: EXPORTAÇÃO ---
        # Salva o arquivo no disco. O formato PNG é obrigatório para manter a transparência e nitidez.
        imagem.save(nome_arquivo)
        
        print("\n" + "="*40)
        print(f"🚀 QR CODE GERADO COM SUCESSO!")
        print(f"📍 Arquivo: {nome_arquivo}")
        print(f"🎨 Estilo: Módulos Pretos com Borda/Fundo Verde")
        print("="*40)

    except Exception as e:
        # Captura erros como falta de bibliotecas (Pillow) ou erro de escrita no disco.
        print(f"\n❌ ERRO CRÍTICO: {e}")
        print("💡 DICA: Verifique se o ambiente virtual (venv) está ativo e o Pillow instalado.")

# --- BLOCO DE EXECUÇÃO ---
if __name__ == "__main__":
    # Digite aqui o que o usuário verá ao escanear:
    meu_texto = "Este QR Code agora tem o fundo verde!"
    
    # Nome do arquivo de saída:
    arquivo_saida = "qrcx_verde.png"
    
    # Chama a função principal
    gerar_qr_code_colorido(meu_texto, arquivo_saida)
