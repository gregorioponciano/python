# Enquanto o os cria pastas, o shutil é o melhor para copiar 
# arquivos e pastas inteiras (como um backup).
import shutil

# 1. Vamos imaginar que queremos copiar um arquivo de log
# (Para testar, você precisaria ter o arquivo 'extrato.txt' na pasta)
try:
    shutil.copy("extrato.txt", "extrato_backup.txt")
    print("Backup do extrato realizado com sucesso!")
except FileNotFoundError:
    print("Erro: O arquivo original não foi encontrado para copiar.")

    # se nao tiver permissao root ou do user
except PermissionError:
    print("Erro: Você não tem permissão para copiar o arquivo.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")