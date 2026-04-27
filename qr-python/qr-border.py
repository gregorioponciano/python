import qrcode
from PIL import Image, ImageOps  # Importamos ferramentas extras para manipular a imagem

def gerar_qr_com_borda_verde(conteudo, nome_arquivo):
    """
    Cria um QR Code clássico (preto e branco) e adiciona uma moldura verde.
    """
    try:
        # --- PASSO 1: CONFIGURAÇÃO DO QR CODE ---
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=0,  # IMPORTANTE: Deixamos 0 aqui para nós criarmos a borda manualmente
        )
        qr.add_data(conteudo)
        qr.make(fit=True)

        # Criamos o QR Code padrão (Preto no Branco)
        # Usamos 'RGB' para permitir cores na edição posterior
        img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # --- PASSO 2: CRIAÇÃO DA BORDA COLORIDA ---
        # Definimos a largura da borda (ex: 20 pixels)
        largura_borda = 30 
        cor_da_borda = "green" # Aqui você define a cor Verde

        # O ImageOps.expand adiciona uma moldura ao redor da imagem existente
        img_final = ImageOps.expand(img_qr, border=largura_borda, fill=cor_da_borda)

        # --- PASSO 3: SALVAMENTO ---
        img_final.save(nome_arquivo)
        
        print(f"\n✅ SUCESSO: QR Code com BORDA VERDE gerado!")
        print(f"📂 Arquivo: {nome_arquivo}")

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("💡 DICA: Certifique-se de que o Pillow está instalado corretamente.")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    # Conteúdo que o QR Code vai mostrar
    meu_conteudo = "QR Code com moldura verde personalizada!"
    
    # Nome do arquivo final
    arquivo_saida = "qrcx_borda_verde.png"
    
    gerar_qr_com_borda_verde(meu_conteudo, arquivo_saida)